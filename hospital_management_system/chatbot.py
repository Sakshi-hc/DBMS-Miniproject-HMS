from datetime import datetime
from .extensions import db

class ChatMessage(db.Model):
    __tablename__ = 'chat_message'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # Null for bot messages
    message = db.Column(db.Text, nullable=False)
    is_bot = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Define relationship with User
    user = db.relationship('User', backref=db.backref('chat_messages', lazy=True))

class Chatbot:
    @staticmethod
    def get_response(message, user_id=None):
        # Store user message
        user_msg = ChatMessage(
            user_id=user_id,
            message=message,
            is_bot=False
        )
        db.session.add(user_msg)
        
        # Convert message to lowercase for easier matching
        message = message.lower()
        
        # Generate response based on message content
        response = Chatbot._generate_response(message)
        
        # Store bot response
        bot_msg = ChatMessage(
            message=response,
            is_bot=True
        )
        db.session.add(bot_msg)
        db.session.commit()
        
        return response
    
    @staticmethod
    def _generate_response(message):
        # Common hospital-related queries and responses
        if any(word in message for word in ['hello', 'hi', 'hey']):
            return "Hello! I'm your hospital assistant. How can I help you today?"
            
        elif any(word in message for word in ['appointment', 'schedule', 'book']):
            return "To schedule an appointment, please go to 'My Appointments' in the navigation bar and click 'Add Appointment'. You can select your preferred doctor and time slot."
            
        elif any(word in message for word in ['bill', 'payment', 'cost', 'fee']):
            return "You can view your bills by going to 'My Bills' in the navigation bar. For payment-related queries, please contact the billing department."
            
        elif any(word in message for word in ['medical record', 'history', 'report']):
            return "Your medical records are available under 'My Medical Records' in the navigation bar. You can view your complete medical history there."
            
        elif any(word in message for word in ['doctor', 'physician']):
            return "You can find information about our doctors under the 'Doctors' section. Each doctor's profile includes their specialization and availability."
            
        elif any(word in message for word in ['emergency', 'urgent']):
            return "For medical emergencies, please call our emergency hotline at 911 or visit the emergency department immediately."
            
        elif any(word in message for word in ['contact', 'phone', 'number']):
            return "You can reach our main reception at (555) 123-4567. For specific departments, please check the 'Contact Us' section on our website."
            
        elif any(word in message for word in ['thank', 'thanks']):
            return "You're welcome! Is there anything else I can help you with?"
            
        elif any(word in message for word in ['bye', 'goodbye']):
            return "Thank you for chatting with me. Take care and stay healthy!"
            
        else:
            return "I'm here to help with hospital-related queries. You can ask me about appointments, bills, medical records, or contact information. How can I assist you?" 