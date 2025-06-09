import os
from telegram import Update
from telegram.ext import ContextTypes
from mindee_api import MindeeClient
from gemini_client import GeminiClient
from database import ChatHistoryDB
import traceback
import re


class InsuranceBot:
    def __init__(self, chat_history_db):
        self.data_dir = "data/documents"
        os.makedirs(self.data_dir, exist_ok=True)
        self.mindee_client = MindeeClient()
        self.gemini_client = GeminiClient()
        self.db: ChatHistoryDB = chat_history_db
        self.prompt = (
            "FOLLOW THE HISTORY!!!! "
            "You are a virtual assistant for an insurance company, operating inside a Telegram bot. "
            "Your job is to politely and clearly help users purchase car insurance. Communicate in a friendly, human-like manner without being too formal. "
            "Follow this strict scenario and do not deviate: "
            "1. Greeting and purpose: Briefly introduce yourself and explain that you're here to help with car insurance. Immediately move to the next step. "
            "2. Request documents: Ask the user to send a photo of their passport. "
            "3. After passport verification: Ask the user to send a photo of their vehicle identification document. "
            "4. Data confirmation: Once both documents are processed, display the extracted information as text. Then ask: "
            "'Please check if everything is correct. If there are any mistakes, you can send either photo again.' "
            "5. Price: If the user confirms the data, reply: 'The insurance price is 100 USD. This is a fixed rate.' Then ask if they are ready to proceed. "
            "6. Completion: If the user agrees, generate a detailed car insurance policy using this template:\n\n"
            "CAR INSURANCE POLICY\n"
            "Policy Number: POL-{CURRENT_YEAR}-{RANDOM_6_DIGITS}\n"
            "Issue Date: {CURRENT_DATE}\n\n"
            "INSURED DETAILS\n"
            "Full Name: [Extract from passport data]\n"
            "Document ID: [Extract from passport data]\n"
            "Address: [Extract from passport data]\n\n"
            "VEHICLE DETAILS\n"
            "Make and Model: [Extract from vehicle document]\n"
            "Vehicle ID/VIN: [Extract from vehicle document]\n"
            "Year: [Extract from vehicle document]\n\n"
            "COVERAGE DETAILS\n"
            "Type: Comprehensive Car Insurance\n"
            "Coverage Period: 12 months from issue date\n"
            "Premium Amount: 100 USD\n"
            "Coverage Includes:\n"
            "- Third Party Liability (up to $100,000)\n"
            "- Collision Damage\n"
            "- Natural Disasters\n"
            "- Theft Protection\n"
            "- 24/7 Roadside Assistance\n\n"
            "TERMS AND CONDITIONS\n"
            "1. This policy is valid for 12 months from the issue date\n"
            "2. Claims must be reported within 24 hours of incident\n"
            "3. Deductible: $500 per claim\n"
            "4. Policy is non-transferable\n"
            "5. Coverage is valid within the territory of operation\n\n"
            "For assistance, contact:\n"
            "Phone: +1-800-INSURE\n"
            "Email: support@carinsurance.com\n"
            "---END OF POLICY---\n\n"
            "After generating the policy, say: 'Here is your insurance policy. Thank you for using our service!'\n\n"
            "⚠️ Handling invalid inputs: If the user says something off-topic (e.g., asks about other insurance types, jokes, is rude, or sends nonsense), reply politely and neutrally. For example: "
            "'I can only help with car insurance. Shall we begin?' "
            "'Please send the required documents to continue.' "
            "'Sorry, I can only assist with car insurance at the moment.' "
            "‼️ Never make up information. Do not pretend to be a real person. Only respond based on known context. If something is unclear — ask the user to clarify. "
            "Additional instructions: "
            "- If the user asks questions related to the car insurance process, such as: "
            "'What kind of insurance is this?' "
            "'How much does it cost?' "
            "'What does the insurance cover?' "
            "or any other reasonable questions about the insurance product or pricing, "
            "answer these questions politely and clearly, then immediately continue with the current step of the scenario without skipping or restarting steps. "
            "- Do not deviate from the scenario flow even after answering such questions. Always bring the user back to the next expected step. "
            "IMPORTANT"
            "Step tracking: After completing any of the 5 scenario steps, include this line exactly once in your reply to indicate the step number:\n"
            "'[STEP COMPLETED: X]' where X = CURRENT STEP + 1, if step was completed.(1-6) (if not completed X=-1). DO NOT DECREASE STEP NUMBER!"
        )

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = str(update.effective_chat.id)
        message = (
            "Hello! I'm your insurance assistant bot. I'll help you purchase car insurance.\n"
            "To get started, please send me a photo of your passport."
        )
        await update.message.reply_text(message)
        await self.db.add_message(chat_id, "/start", message)
        await self.db.set_step_passed(chat_id, 1)

    async def unknown(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "Sorry, I don't understand that command. Please send /start to begin the insurance process."
        )

    async def handle_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = str(update.effective_chat.id)
        current_step = await self.db.get_step_passed(chat_id)

        if not update.message.photo:
            await update.message.reply_text("Please send a photo of the required document.")
            return

        # Determine document type based on current step
        doc_type = "passport" if current_step < 3 else "vehicle"

        photo = update.message.photo[-1]
        file_id = photo.file_id

        try:
            file = await context.bot.get_file(file_id)
            downloaded_file = await file.download_as_bytearray()

            local_path = f"{self.data_dir}/{file_id}.jpg"
            with open(local_path, "wb") as f:
                f.write(downloaded_file)

            print(f"Saved photo to: {local_path}")
            await update.message.reply_text(f"Photo received, processing {doc_type}...")

            try:
                mindee_result = await self.mindee_client.recognize_document(local_path, doc_type)
                if not mindee_result:
                    await update.message.reply_text(f"Could not extract data from the {doc_type}. Please try again with a clearer photo.")
                    return

                # Store the extracted data
                await self.db.set_document_data(chat_id, doc_type, mindee_result)

                if current_step < 3:
                    # After passport, ask for vehicle document
                    response = (
                        f"Passport data processed successfully.\n\n"
                        f"Extracted text:\n{mindee_result.get('full_text', 'No text extracted')}\n\n"
                        f"Now, please send a photo of your vehicle identification document."
                    )
                    await self.db.set_step_passed(chat_id, 3)
                else:
                    # Both documents processed, show all data
                    passport_data = await self.db.get_document_data(chat_id, "passport")
                    vehicle_data = mindee_result
                    
                    response = (
                        "Here's all the extracted information:\n\n"
                        f"Passport Data:\n{passport_data.get('full_text', 'No text extracted')}\n\n"
                        f"Vehicle Data:\n{vehicle_data.get('full_text', 'No text extracted')}\n\n"
                        "Please confirm if all information is correct. If not, you can resend either document."
                    )
                    await self.db.set_step_passed(chat_id, 4)

                await update.message.reply_text(response)
                await self.db.add_message(chat_id, f"SYSTEM:**{doc_type.capitalize()} photo sent**", response)

            except Exception as e:
                print(f"Mindee API error: {str(e)}")
                await update.message.reply_text(f"Error processing the {doc_type}: {str(e)}. Please try again with a clearer photo.")
                return

        except Exception as e:
            print(f"Error downloading or saving photo: {str(e)}")
            await update.message.reply_text("Error saving the photo. Please try again.")

    async def handle_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = str(update.effective_chat.id)
        user_input = update.message.text
        
        chat_history = "Chat History:\n"
        chat_history += await self.db.get_trimmed_chat_history(chat_id)
        chat_history += f"User:{user_input} **THIS IS THE LAST MESSAGE FROM USER YOU HAVE TO ANSWER**\n"     
        chat_history += "HISTORY ENDS"
        
        final_prompt = self.prompt + f"\nCURRENT STEP = {await self.db.get_step_passed(chat_id)}"
        gemini_input = chat_history + "\n" + final_prompt 
        gemini_response = self.gemini_client.communicate(gemini_input)
        
        print(f"GEMINI response: {gemini_response}")
        match = re.search(r"\[STEP COMPLETED: (-?\d)\]", gemini_response)
        if match:
            step_passed = int(match.group(1))
            if (step_passed != -1):
                await self.db.set_step_passed(chat_id, step_passed)
            print(f"Step completed: {step_passed}")
            print(f"Step passed: {await self.db.get_step_passed(chat_id)}")
            gemini_response = re.sub(r"\[STEP COMPLETED: -?\d+\]", "", gemini_response).strip()

        await update.message.reply_text(gemini_response)
        await self.db.add_message(chat_id, user_input, gemini_response)

    