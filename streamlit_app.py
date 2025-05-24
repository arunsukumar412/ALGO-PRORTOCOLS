import streamlit as st
import random
from datetime import datetime, timedelta
from typing import List, Dict
import json
import os
import pandas as pd # For displaying data in a nice table

# --- File for storing submissions ---
SUBMISSIONS_FILE = "submissions.json"

class LegacyJavaCodeChallenge:
    def __init__(self):
        self.code_samples = self._load_java_code_samples()
        # Stricter evaluation criteria weights
        self.evaluation_criteria = {
            'correct_requirements': 0.75,
            'identified_bugs': 0.15,
            'code_improvements': 0.10
        }

    def _load_java_code_samples(self) -> List[Dict]:
        """Load various buggy Java code samples with hidden requirements"""
        return [
            # NEW EASY CHALLENGE
            {
                'id': 0,
                'name': "Simple Calculator Bug Fix",
                'difficulty': "Easy",
                'code': """
public class Calculator {
    public int add(int a, int b) {
        return a + b;
    }

    public int subtract(int a, int b) {
        return a - b;
    }

    public int multiply(int a, int b) {
        return a * b;
    }

    public double divide(int a, int b) {
        return a / b;
    }
}
                """,
                'hints': [
                    "Basic arithmetic operations",
                    "Look for potential issues with division",
                    "Consider edge cases for input values"
                ],
                'expected_requirements': [
                    "Handles addition of two integers",
                    "Handles subtraction of two integers",
                    "Handles multiplication of two integers",
                    "Handles division of two integers (non-zero denominator)",
                    "Returns correct results for positive numbers",
                    "Returns correct results for negative numbers",
                    "Handles division by zero gracefully" # Added this one for the bug
                ]
            },
            {
                'id': 1,
                'name': "Multi-Layer Authentication System",
                'difficulty': "Hard",
                'code': """
public class AuthenticationService {
    private static final Map<String, String> VALID_USERS = Map.of(
        "admin", "Secure123",
        "user1", "Password1"
    );

    public boolean authenticateUser(String username, String password, String otp, boolean biometric) {
        if (!VALID_USERS.containsKey(username) || !VALID_USERS.get(username).equalsIgnoreCase(password)) {
            return false;
        }

        if (otp != null) {
            try {
                int otpValue = Integer.parseInt(otp);
                if (otpValue < 100000 || otpValue > 999999) {
                    return false;
                }
            } catch (NumberFormatException e) {
                return false;
            }
        }

        if (biometric) {
            return Math.random() > 0.1;
        }

        return true;
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
                    "Proper biometric verification",
                    "Failed login attempt logging",
                    "Minimum 2FA requirement",
                    "Null checks for parameters",
                    "Thread-safe implementation"
                ]
            },
            {
                'id': 2,
                'name': "Distributed Transaction Handler",
                'difficulty': "Expert",
                'code': """
public class TransactionHandler {
    private Map<String, Map<String, Double>> accounts = Map.of(
        "user1", Map.of("USD", 1000.0, "EUR", 500.0),
        "user2", Map.of("USD", 2000.0, "EUR", 300.0)
    );

    public TransactionResult handleTransaction(String sender, String receiver,
                                              double amount, String currency) {
        try {
            if (accounts.get(sender).get(currency) < amount) {
                return new TransactionResult(false, "Insufficient funds");
            }

            accounts.get(sender).put(currency,
                accounts.get(sender).get(currency) - amount);
            accounts.get(receiver).put(currency,
                accounts.get(receiver).get(currency) + amount);

            return new TransactionResult(true, "Success");
        } catch (NullPointerException e) {
            return new TransactionResult(false, "Account not found");
        }
    }
}
                """,
                'hints': [
                    "Handles financial transactions between accounts",
                    "Consider all edge cases in financial operations",
                    "Think about concurrent access to accounts"
                ],
                'expected_requirements': [
                    "Transaction ID generation",
                    "Atomic transaction handling",
                    "Currency conversion support",
                    "Overdraft protection",
                    "Detailed error messages",
                    "Transaction logging",
                    "Concurrency control",
                    "Input validation"
                ]
            }
        ]

    def get_random_challenge(self) -> Dict:
        """Select a random Java code challenge, prioritizing 'Easy' ones."""
        easy_challenges = [c for c in self.code_samples if c['difficulty'] == "Easy"]
        if easy_challenges:
            return random.choice(easy_challenges)
        return random.choice(self.code_samples) # Fallback

    def evaluate_response(self, challenge_id: int,
                          requirements: List[str],
                          bugs: List[str],
                          improvements: List[str]) -> float:
        """Evaluate candidate's response based on stricter criteria"""
        challenge = next(c for c in self.code_samples if c['id'] == challenge_id)

        req_matches = sum(1 for req in requirements
                          if req in challenge['expected_requirements'])
        req_score = req_matches / len(challenge['expected_requirements'])

        # Stricter thresholds for bugs and improvements
        bug_threshold = 5 # Now requires 5 identified bugs for full bug score
        bug_score = min(1.0, len(bugs) / bug_threshold)

        imp_threshold = 5 # Now requires 5 suggested improvements for full improvement score
        imp_score = min(1.0, len(improvements) / imp_threshold)

        total_score = (
            req_score * self.evaluation_criteria['correct_requirements'] +
            bug_score * self.evaluation_criteria['identified_bugs'] +
            imp_score * self.evaluation_criteria['code_improvements']
        )

        return round(total_score, 2)

# --- NEW: Functions for Local JSON Data Storage ---
def save_submission_data(data: Dict):
    """Appends a new submission record to the JSON file."""
    if not os.path.exists(SUBMISSIONS_FILE):
        with open(SUBMISSIONS_FILE, 'w') as f:
            json.dump([], f) # Initialize as an empty list if file doesn't exist

    with open(SUBMISSIONS_FILE, 'r+') as f:
        file_data = json.load(f)
        file_data.append(data)
        f.seek(0) # Rewind to the beginning
        json.dump(file_data, f, indent=4)
        f.truncate() # Remove remaining part


def load_all_submission_data() -> List[Dict]:
    """Loads all submission records from the JSON file."""
    if not os.path.exists(SUBMISSIONS_FILE):
        return []
    with open(SUBMISSIONS_FILE, 'r') as f:
        return json.load(f)
# --- END NEW: Functions for Local JSON Data Storage ---


def main():
    st.set_page_config(page_title="Java Legacy Code Challenge", layout="wide")

    # Initialize session state variables
    if 'challenge' not in st.session_state:
        st.session_state.challenge = None
        st.session_state.show_hints = False
        st.session_state.submitted = False # True when a challenge has been submitted
        st.session_state.candidate_email = ""
        st.session_state.team_name = ""
        st.session_state.start_time = None
        st.session_state.time_up = False
        st.session_state.current_question = 0
        st.session_state.requirements = ""
        st.session_state.bugs = ""
        st.session_state.improvements = ""
        st.session_state.answers_saved = False
        st.session_state.last_submission_details = None # New: To store details for immediate display

    challenge_system = LegacyJavaCodeChallenge()

    st.title("☕ Java Legacy Code Challenge")
    st.markdown("""
    ### Time Limit: 45 minutes
    Analyze the Java code and:
    1. Identify requirements
    2. Find bugs
    3. Suggest improvements
    """)

    # Timer display for challenge duration
    if st.session_state.start_time and not st.session_state.time_up and not st.session_state.submitted:
        elapsed = datetime.now() - st.session_state.start_time
        remaining = timedelta(minutes=45) - elapsed
        if remaining.total_seconds() <= 0:
            st.session_state.time_up = True
            st.error("⏰ Time's up! Your answers are saved, please click 'Submit Final' if you haven't yet.")
            st.rerun() # Rerun to update state
        else:
            mins, secs = divmod(int(remaining.total_seconds()), 60)
            st.warning(f"⏱️ Time left: {mins:02d}:{secs:02d}")

    # Sidebar
    with st.sidebar:
        st.header("Team Info")
        st.session_state.team_name = st.text_input("Team Name (Required)", value=st.session_state.team_name)
        st.session_state.candidate_email = st.text_input("Your Email (Required)", value=st.session_state.candidate_email)

        st.header("Controls")
        if st.button("🎯 New Challenge"):
            if not st.session_state.team_name or not st.session_state.candidate_email:
                st.error("Please provide team name and email before starting a new challenge.")
                st.stop()
            st.session_state.challenge = challenge_system.get_random_challenge()
            st.session_state.show_hints = False
            st.session_state.submitted = False
            st.session_state.start_time = datetime.now()
            st.session_state.time_up = False
            st.session_state.current_question = 0
            st.session_state.requirements = ""
            st.session_state.bugs = ""
            st.session_state.improvements = ""
            st.session_state.answers_saved = False
            st.session_state.last_submission_details = None # Reset for new challenge
            st.rerun()

        if st.session_state.challenge and st.button("💡 Toggle Hints"):
            st.session_state.show_hints = not st.session_state.show_hints
            st.rerun()

        st.markdown("---")
        st.header("Admin View")
        if st.button("📈 Show All Scores (Admin Only)"):
            st.session_state.show_admin_dashboard = True
            st.session_state.submitted = False # Hide personal submission if looking at admin
            st.rerun()
        if st.session_state.get('show_admin_dashboard', False) and st.button("Hide Admin View"):
            st.session_state.show_admin_dashboard = False
            st.rerun()

    # --- Admin Dashboard Display Logic ---
    if st.session_state.get('show_admin_dashboard', False):
        st.subheader("📊 All Challenge Submissions (Admin Dashboard)")
        all_submissions = load_all_submission_data()

        if not all_submissions:
            st.info("No submissions recorded yet.")
        else:
            # Create a DataFrame for better display
            df = pd.DataFrame(all_submissions)
            # Optionally, select/reorder columns for display
            display_cols = [
                'submission_time', 'team_name', 'candidate_email',
                'challenge_name', 'score', 'requirements', 'bugs', 'improvements'
            ]
            # Ensure all display_cols exist, fill missing with empty string
            for col in display_cols:
                if col not in df.columns:
                    df[col] = ''
            df['submission_time'] = pd.to_datetime(df['submission_time']).dt.strftime('%Y-%m-%d %H:%M:%S')

            st.dataframe(df[display_cols].set_index('submission_time'), use_container_width=True)

            # Option to download data
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download All Submissions as CSV",
                data=csv,
                file_name="all_challenge_submissions.csv",
                mime="text/csv",
            )
        st.stop() # Stop further execution of main loop to show only dashboard

    # --- Individual Challenge & Submission Logic ---
    if st.session_state.submitted:
        # Display individual score immediately
        st.subheader("✅ Submission Complete!")
        if st.session_state.last_submission_details:
            details = st.session_state.last_submission_details
            st.metric(label="Your Score", value=f"{details['score']*100:.1f}/100")
            st.info(f"**Challenge:** {details['challenge_name']}")
            st.info(f"**Team Name:** {details['team_name']}")
            st.info(f"**Candidate Email:** {details['candidate_email']}")


            st.subheader("Your Identified Requirements:")
            st.markdown(f"```\n{details['requirements']}\n```")

            st.subheader("Your Found Bugs:")
            st.markdown(f"```\n{details['bugs']}\n```")

            st.subheader("Your Suggested Improvements:")
            st.markdown(f"```\n{details['improvements']}\n```")
        else:
            st.info("No submission details available for this session. Please complete a challenge.")

        if st.button("🔄 Try Another Challenge"):
            st.session_state.challenge = None # Clear challenge to reset state
            st.session_state.show_hints = False
            st.session_state.submitted = False
            st.session_state.start_time = None
            st.session_state.time_up = False
            st.session_state.current_question = 0
            st.session_state.requirements = ""
            st.session_state.bugs = ""
            st.session_state.improvements = ""
            st.session_state.answers_saved = False
            st.session_state.last_submission_details = None
            st.session_state.show_admin_dashboard = False # Ensure admin dashboard is hidden
            st.rerun()

    elif st.session_state.challenge: # Challenge is active and not submitted
        challenge = st.session_state.challenge
        st.subheader(f"🧩 {challenge['name']} ({challenge['difficulty']})")

        with st.expander("📜 View Java Code", expanded=True):
            st.code(challenge['code'], language='java')

        if st.session_state.show_hints:
            st.subheader("❓ Hints")
            for hint in challenge['hints']:
                st.write(f"- {hint}")

        # Questions navigation and form
        questions = [
            {"title": "1. Requirements (one per line)", "key": "requirements"},
            {"title": "2. Bugs (one per line)", "key": "bugs"},
            {"title": "3. Improvements (one per line)", "key": "improvements"}
        ]

        st.progress((st.session_state.current_question + 1) / len(questions))
        st.caption(f"Question {st.session_state.current_question + 1} of {len(questions)}")

        col1, col2 = st.columns([1, 1])
        with col1:
            if st.session_state.current_question > 0 and st.button("⬅️ Previous"):
                setattr(st.session_state, questions[st.session_state.current_question]["key"],
                        st.session_state[f"answer_{questions[st.session_state.current_question]['key']}"])
                st.session_state.current_question -= 1
                st.rerun()
        with col2:
            next_disabled = not st.session_state.answers_saved and st.session_state.current_question < len(questions) - 1
            if st.session_state.current_question < len(questions) - 1 and st.button("➡️ Next", disabled=next_disabled):
                setattr(st.session_state, questions[st.session_state.current_question]["key"],
                        st.session_state[f"answer_{questions[st.session_state.current_question]['key']}"])
                st.session_state.current_question += 1
                st.session_state.answers_saved = False
                st.rerun()

        with st.form(f"question_form_{st.session_state.current_question}"):
            current_q = questions[st.session_state.current_question]
            st.subheader(current_q["title"])

            answer_key = f"answer_{current_q['key']}"
            if answer_key not in st.session_state:
                st.session_state[answer_key] = getattr(st.session_state, current_q["key"])

            answer = st.text_area(
                "Your answer",
                value=st.session_state[answer_key],
                height=150,
                key=answer_key
            )

            submit_label = "🚀 Submit Final" if st.session_state.current_question == len(questions) - 1 else "💾 Save Answer"
            submitted = st.form_submit_button(submit_label)

            if submitted:
                if not st.session_state.team_name or not st.session_state.candidate_email:
                    st.error("❗ Please provide team name and your email in the sidebar to proceed.")
                    st.stop()

                setattr(st.session_state, current_q["key"], answer)
                st.session_state.answers_saved = True

                if st.session_state.current_question == len(questions) - 1:
                    st.session_state.submitted = True
                    st.session_state.time_up = True

                    score = challenge_system.evaluate_response(
                        st.session_state.challenge['id'],
                        [r.strip() for r in st.session_state.requirements.split('\n') if r.strip()],
                        [b.strip() for b in st.session_state.bugs.split('\n') if b.strip()],
                        [i.strip() for i in st.session_state.improvements.split('\n') if i.strip()]
                    )

                    # Prepare data for immediate display and persistence
                    submission_data = {
                        "submission_time": datetime.now().isoformat(),
                        "team_name": st.session_state.team_name,
                        "candidate_email": st.session_state.candidate_email,
                        "challenge_name": st.session_state.challenge['name'],
                        "challenge_difficulty": st.session_state.challenge['difficulty'],
                        "score": score,
                        "requirements": st.session_state.requirements,
                        "bugs": st.session_state.bugs,
                        "improvements": st.session_state.improvements
                    }
                    st.session_state.last_submission_details = submission_data

                    # Save to local JSON file
                    save_submission_data(submission_data)
                    st.success("🎉 Your submission is complete!")
                    st.rerun() # Rerun to show the immediate results
                else:
                    st.success("✅ Answer saved! You can now navigate to the next question.")
                    st.rerun()

    # Initial state (no challenge started yet)
    if not st.session_state.challenge and not st.session_state.submitted and not st.session_state.get('show_admin_dashboard', False):
        st.info("👈 Enter team info and click '🎯 New Challenge' to begin!")

if __name__ == "__main__":
    main()
