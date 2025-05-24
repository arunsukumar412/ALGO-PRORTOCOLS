import streamlit as st
import random
from datetime import datetime, timedelta
from typing import List, Dict
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import requests
from fpdf import FPDF
import urllib.parse
import time
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Google Sheets setup
def get_google_sheet():
    scope = ["https://spreadsheets.google.com/feeds", 
             "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_key("11Y2G8gkLbA4PUtd_tqEMIXfXUKBnLym85wjap17Q1Kg").sheet1
    return sheet

class LegacyJavaCodeChallenge:
    def __init__(self):
        self.code_samples = self._load_java_code_samples()
        self.evaluation_criteria = {
            'correct_requirements': 0.5,
            'identified_bugs': 0.4,
            'code_improvements': 0.1
        }
    
    def _load_java_code_samples(self) -> List[Dict]:
        """Load various buggy Java code samples with hidden requirements"""
        return [
            {
                'id': 1,
                'name': "Simple Calculator",
                'difficulty': "Easy",
                'code': """
public class Calculator {
    // Bug: No input validation
    public double add(double a, double b) {
        return a + b; // Bug: No overflow check
    }
    
    public double subtract(double a, double b) {
        return a - b; // Bug: No underflow check
    }
    
    // Bug: Division by zero not handled
    public double divide(double a, double b) {
        return a / b;
    }
    
    public double multiply(double a, double b) {
        return a * b; // Bug: No overflow check
    }
    
    // Bug: No documentation
    public double power(double base, double exponent) {
        return Math.pow(base, exponent); // Bug: No NaN/infinity checks
    }
}
                """,
                'hints': [
                    "Basic arithmetic operations",
                    "Check for mathematical edge cases",
                    "Consider numerical limitations"
                ],
                'expected_requirements': [
                    "Addition with overflow check",
                    "Subtraction with underflow check",
                    "Division with zero check",
                    "Multiplication with overflow check",
                    "Power function with validation",
                    "Input validation for all methods",
                    "Proper method documentation"
                ]
            },
            {
                'id': 2,
                'name': "Multi-Layer Authentication System",
                'difficulty': "Hard",
                'code': """
public class AuthenticationService {
    // Bug: Password check is case-insensitive (security issue)
    private static final Map<String, String> VALID_USERS = Map.of(
        "admin", "Secure123",
        "user1", "Password1"
    );

    public boolean authenticateUser(String username, String password, String otp, boolean biometric) {
        // Bug: No null checks for required parameters
        if (!VALID_USERS.containsKey(username) || !VALID_USERS.get(username).equalsIgnoreCase(password)) {
            return false; // Bug: Should log failed attempts
        }

        if (otp != null) {
            // Bug: OTP validation missing timeout check
            try {
                int otpValue = Integer.parseInt(otp);
                if (otpValue < 100000 || otpValue > 999999) {
                    return false;
                }
            } catch (NumberFormatException e) {
                return false; // Bug: Should log this error
            }
        }

        if (biometric) {
            // Bug: No actual biometric verification
            return Math.random() > 0.1; // 10% failure rate
        }

        return true; // Bug: Should require at least 2FA for sensitive operations
    }
}
                """,
                'hints': [
                    "Security system with multiple authentication layers",
                    "Check for proper validation in each step",
                    "Consider thread safety for the service"
                ],
                'expected_requirements': [
                    "Case-sensitive password validation",
                    "OTP should be 6 digits with timeout",
                    "Proper biometric verification implementation",
                    "Failed login attempt logging",
                    "Minimum 2FA requirement for sensitive operations",
                    "Null checks for required parameters",
                    "Thread-safe implementation"
                ]
            }
        ]
    
    def get_challenge_by_difficulty(self, difficulty: str) -> Dict:
        """Select a challenge by difficulty level"""
        filtered = [c for c in self.code_samples if c['difficulty'].lower() == difficulty.lower()]
        return random.choice(filtered) if filtered else None
    
    def evaluate_response(self, challenge_id: int, 
                         requirements: List[str], 
                         bugs: List[str],
                         improvements: List[str]) -> float:
        """
        Evaluate candidate's response against expected results
        Returns a score between 0 and 1
        """
        challenge = next(c for c in self.code_samples if c['id'] == challenge_id)
        
        # Check how many requirements were identified
        req_matches = sum(1 for req in requirements 
                         if req in challenge['expected_requirements'])
        req_score = req_matches / len(challenge['expected_requirements'])
        
        # Check if major bugs were identified
        bug_score = min(1.0, len(bugs) / 3)  # More bugs identified = higher score
        
        # Give credit for improvements
        imp_score = min(1.0, len(improvements) / 3)
        
        total_score = (
            req_score * self.evaluation_criteria['correct_requirements'] +
            bug_score * self.evaluation_criteria['identified_bugs'] +
            imp_score * self.evaluation_criteria['code_improvements']
        )
        
        return round(total_score, 2)

def create_pdf(team_name: str, candidate_email: str, challenge_name: str, 
               requirements: str, bugs: str, improvements: str, score: float) -> bytes:
    """Create a PDF report of the candidate's response"""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Title
    pdf.cell(200, 10, txt="Java Legacy Code Challenge Results", ln=1, align="C")
    pdf.ln(10)
    
    # Basic info
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(40, 10, txt="Team Name:", ln=0)
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, txt=team_name, ln=1)
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(40, 10, txt="Candidate Email:", ln=0)
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, txt=candidate_email, ln=1)
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(40, 10, txt="Challenge:", ln=0)
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, txt=challenge_name, ln=1)
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(40, 10, txt="Score:", ln=0)
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, txt=f"{score*100:.1f}/100", ln=1)
    pdf.ln(10)
    
    # Requirements section
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, txt="Requirements Identified:", ln=1)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, txt=requirements)
    pdf.ln(5)
    
    # Bugs section
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, txt="Bugs Found:", ln=1)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, txt=bugs)
    pdf.ln(5)
    
    # Improvements section
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, txt="Suggested Improvements:", ln=1)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, txt=improvements)
    
    return pdf.output(dest='S').encode('latin1')

def save_to_google_sheet(team_name: str, candidate_email: str, challenge_name: str, 
                        requirements: str, bugs: str, improvements: str, score: float):
    """Save the response data to Google Sheets"""
    try:
        sheet = get_google_sheet()
        
        # Prepare the data row
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data_row = [
            timestamp,
            team_name,
            candidate_email,
            challenge_name,
            requirements,
            bugs,
            improvements,
            f"{score*100:.1f}"
        ]
        
        # Append the row to the sheet
        sheet.append_row(data_row)
        return True
    except Exception as e:
        st.error(f"Error saving to Google Sheet: {str(e)}")
        return False

def send_email_with_pdf(team_name: str, candidate_email: str, challenge_name: str, 
                       requirements: str, bugs: str, improvements: str, score: float):
    """Send the candidate's response via email with PDF attachment"""
    sender_email = "your.email@gmail.com"  # Replace with your email
    sender_password = "your_app_password"  # Use app password for Gmail
    receiver_email = "arunsukumar03@gmail.com"
    
    # Create PDF
    pdf_bytes = create_pdf(team_name, candidate_email, challenge_name, 
                          requirements, bugs, improvements, score)
    
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = f"[Java Code Challenge] {team_name} - {challenge_name}"
    
    body = f"""
    Team Name: {team_name}
    Candidate Email: {candidate_email}
    Challenge: {challenge_name}
    Score: {score*100:.1f}/100
    
    See attached PDF for detailed analysis.
    """
    
    message.attach(MIMEText(body, "plain"))
    
    # Attach PDF
    pdf_attachment = MIMEApplication(pdf_bytes, _subtype="pdf")
    pdf_attachment.add_header('Content-Disposition', 'attachment', 
                            filename=f"JavaChallenge_{team_name}.pdf")
    message.attach(pdf_attachment)
    
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, message.as_string())
        return True
    except Exception as e:
        st.error(f"Failed to send email: {e}")
        return False

def display_timer(start_time, time_limit_minutes):
    """Display a countdown timer"""
    if start_time:
        elapsed = datetime.now() - start_time
        remaining = timedelta(minutes=time_limit_minutes) - elapsed
        if remaining.total_seconds() <= 0:
            return True, "00:00:00"  # Time's up
        else:
            hours, remainder = divmod(int(remaining.total_seconds()), 3600)
            minutes, seconds = divmod(remainder, 60)
            return False, f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    return False, "45:00"  # Default display

def main():
    st.set_page_config(page_title="Java Legacy Code Challenge", layout="wide")
    
    # Initialize session state
    if 'challenge' not in st.session_state:
        st.session_state.challenge = None
        st.session_state.show_hints = False
        st.session_state.submitted = False
        st.session_state.candidate_email = ""
        st.session_state.team_name = ""
        st.session_state.start_time = None
        st.session_state.time_up = False
        st.session_state.difficulty = "Easy"
    
    challenge_system = LegacyJavaCodeChallenge()
    
    st.title("☕ Java Legacy Code Challenge")
    st.markdown("""
    ### You have 45 minutes to complete this challenge!
    Analyze the buggy Java legacy code and:
    1. Deduce the original requirements
    2. Identify all bugs
    3. Suggest improvements
    
    *Results will be saved to Google Sheets and sent as PDF to arunsukumar03@gmail.com*
    """)
    
    # Timer display
    if st.session_state.start_time:
        time_up, timer_text = display_timer(st.session_state.start_time, 45)
        if time_up:
            st.session_state.time_up = True
            st.error("⏰ Time's up! Submissions are now closed.")
        else:
            st.warning(f"⏱️ Time remaining: {timer_text}")
    
    # Sidebar for team info and controls
    with st.sidebar:
        st.header("Team Information")
        st.session_state.team_name = st.text_input("Team Name (Required)")
        st.session_state.candidate_email = st.text_input("Your Email (Required)")
        st.session_state.difficulty = st.selectbox(
            "Challenge Difficulty",
            ["Easy", "Hard"],
            index=0 if st.session_state.difficulty == "Easy" else 1
        )
        
        st.header("Challenge Controls")
        if st.button("🎯 Get Challenge"):
            st.session_state.challenge = challenge_system.get_challenge_by_difficulty(
                st.session_state.difficulty
            )
            st.session_state.show_hints = False
            st.session_state.submitted = False
            st.session_state.start_time = datetime.now()
            st.session_state.time_up = False
            st.rerun()
        
        if st.session_state.challenge:
            if st.button("💡 Toggle Hints"):
                st.session_state.show_hints = not st.session_state.show_hints
                st.rerun()
    
    # Display challenge if available and time not up
    if st.session_state.challenge and not st.session_state.time_up:
        challenge = st.session_state.challenge
        st.subheader(f"🧩 {challenge['name']} ({challenge['difficulty']} Level)")
        
        with st.expander("📜 View Java Code", expanded=True):
            st.code(challenge['code'], language='java')
        
        if st.session_state.show_hints:
            st.subheader("❓ Hints")
            for hint in challenge['hints']:
                st.write(f"- {hint}")
    
    # Response form (only if time hasn't expired)
    if st.session_state.challenge and not st.session_state.submitted and not st.session_state.time_up:
        with st.form("response_form"):
            st.subheader("🔍 Your Analysis")
            
            requirements = st.text_area(
                "1. Deduced requirements (one per line)",
                help="What were the original requirements for this code?",
                height=150
            )
            
            bugs = st.text_area(
                "2. Identified bugs (one per line)",
                help="List all bugs you've found with explanations",
                height=150
            )
            
            improvements = st.text_area(
                "3. Suggested improvements (one per line)",
                help="How would you improve this code?",
                height=150
            )
            
            submitted = st.form_submit_button("🚀 Submit Analysis")
            
            if submitted:
                if not st.session_state.team_name or not st.session_state.candidate_email:
                    st.error("Please provide both team name and email address")
                    st.stop()
                
                st.session_state.submitted = True
                score = challenge_system.evaluate_response(
                    st.session_state.challenge['id'],
                    [r.strip() for r in requirements.split('\n') if r.strip()],
                    [b.strip() for b in bugs.split('\n') if b.strip()],
                    [i.strip() for i in improvements.split('\n') if i.strip()]
                )
                
                # Save to Google Sheet
                with st.spinner("Saving to Google Sheets..."):
                    sheet_saved = save_to_google_sheet(
                        st.session_state.team_name,
                        st.session_state.candidate_email,
                        st.session_state.challenge['name'],
                        requirements,
                        bugs,
                        improvements,
                        score
                    )
                
                # Send email with PDF
                with st.spinner("Sending email with PDF..."):
                    email_sent = send_email_with_pdf(
                        st.session_state.team_name,
                        st.session_state.candidate_email,
                        st.session_state.challenge['name'],
                        requirements,
                        bugs,
                        improvements,
                        score
                    )
                
                if sheet_saved and email_sent:
                    st.success("📊 Your response has been saved to Google Sheets and emailed as PDF!")
                elif not sheet_saved and email_sent:
                    st.warning("⚠️ Email sent but Google Sheets save failed")
                elif sheet_saved and not email_sent:
                    st.warning("⚠️ Saved to Google Sheets but email failed")
                else:
                    st.error("❌ Both submissions failed - please try again")
                
                st.rerun()
    
    # Show confirmation if submitted
    if st.session_state.submitted:
        st.subheader("📨 Submission Confirmation")
        
        if st.button("🔄 Try Another Challenge"):
            st.session_state.challenge = None
            st.session_state.show_hints = False
            st.session_state.submitted = False
            st.rerun()
    
    # Initial state - no challenge selected
    if not st.session_state.challenge:
        st.info("👈 Enter your team info, select difficulty, and click 'Get Challenge' to begin")

if __name__ == "__main__":
    main()
