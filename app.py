"""
LoanVerse AI - Streamlit Frontend
==================================
Main application entrypoint for the LoanVerse AI conversational loan platform.

Features:
- 7-Phase conversational flow with Maya AI
- Glassmorphism UI Design
- Real-Time Agent Workflow Visualisation
- Live EMI Calculator with donut chart
- Mock E-KYC & Underwriting Engine
- RBI-compliant PDF Sanction Letter Download
"""

import streamlit as st
import time
from datetime import datetime
from typing import Optional, Dict
import os
import plotly.graph_objects as go

from logic import (
    get_user, get_user_with_name_check, check_eligibility, verify_kyc,
    calculate_emi, get_risk_based_rate, get_goldilocks_options
)
from agents.master import MasterAgent, Intent
from assets.sanction_generator import generate_sanction_letter
from assets.avatars import MAYA_AVATAR, USER_AVATAR
from conversation_templates import templates
from enum import Enum

# ============================================================================
# CONVERSATION PHASE DEFINITIONS
# ============================================================================

class ConversationPhase(Enum):
    PHASE_1_WARM_OPENING = "warm_opening"
    PHASE_2_PURPOSE_DISCOVERY = "purpose_discovery"
    PHASE_3_VERIFICATION = "verification"
    PHASE_4_NEEDS_ANALYSIS = "needs_analysis"
    PHASE_5_OPTIONS_PRESENTATION = "options_presentation"
    PHASE_6_CONFIRMATION = "confirmation"
    PHASE_7_DOCUMENTATION = "documentation"


# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="LoanVerse AI - Maya",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CSS STYLING
# ============================================================================

def load_custom_css_file():
    """Load custom CSS assets with theme support."""
    # 1. Load Base Styles
    base_css = os.path.join(os.path.dirname(__file__), "assets", "style.css")
    if os.path.exists(base_css):
        with open(base_css, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
            
    # 2. Load Theme-Specific CSS (Dark or Light Mode)
    if 'theme' not in st.session_state:
        st.session_state.theme = "dark"  # Default to dark mode
    
    if st.session_state.theme == "light":
        theme_css = os.path.join(os.path.dirname(__file__), "assets", "light_mode.css")
    else:
        theme_css = os.path.join(os.path.dirname(__file__), "assets", "bliss_mode.css")
    
    if os.path.exists(theme_css):
        with open(theme_css, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_custom_css_file()


# ============================================================================
# INCLUSIVE UI COMPONENTS
# ============================================================================

def create_emi_donut_chart(principal: float, total_interest: float) -> go.Figure:
    """
    Create donut chart showing Principal vs Interest - matching reference design.
    Blue for Principal,  Orange for Interest.
    """
    fig = go.Figure(data=[go.Pie(
        labels=['■ Principal', '■ Total Interest'],
        values=[principal, total_interest],
        hole=0.6,  # Donut hole size
        marker=dict(
            colors=['#2563EB', '#FB923C'],  # Blue for principal, Orange for interest
            line=dict(color='#ffffff', width=2)
        ),
        textinfo='percent',
        textfont=dict(size=16, family='Poppins, sans-serif', color='white', weight='bold'),
        hovertemplate='<b>%{label}</b><br>₹%{value:,.0f}<br>%{percent}<extra></extra>'
    )])
    
    # Total in center
    total = principal + total_interest
    
    fig.update_layout(
        showlegend=True,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Poppins, sans-serif', size=14, color='#1F2937'),
        height=280,  # Reduced for one-screen fit
        margin=dict(t=10, b=50, l=10, r=10),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.25,
            xanchor="center",
            x=0.5,
            font=dict(size=13, color='#1F2937')
        ),
        annotations=[dict(
            text=f'<b>Total:</b><br>₹{total:,.0f}',
            x=0.5, y=0.5,
            font=dict(size=15, family='Poppins', color='#1F2937', weight='bold'),
            showarrow=False
        )]
    )
    
    return fig

# ============================================================================
# UI HELPER FUNCTIONS
# ============================================================================

def get_dynamic_greeting():
    """Generate dynamic greeting based on time of day and user name."""
    from datetime import datetime
    
    # Get current hour
    current_hour = datetime.now().hour
    
    # Determine greeting based on time
    if 5 <= current_hour < 12:
        time_greeting = "Good morning"
    elif 12 <= current_hour < 17:
        time_greeting = "Good afternoon"
    else:
        time_greeting = "Good evening"
    
    # Get user name from session state if available
    user_name = "Guest"
    if st.session_state.get('user_data') and st.session_state.user_data.get('name'):
        user_name = st.session_state.user_data['name'].split()[0]  # First name only
    
    return f"{time_greeting}, {user_name}"

def render_emi_hero(loan_amount: float, tenure_months: int, rate: float):
    """Render hero EMI metric with glassmorphism design."""
    emi = calculate_emi(loan_amount, tenure_months, rate)
    
    hero_html = f"""
    <div class="hero-metric">
        <div class="label">Your Monthly EMI</div>
        <div class="emi-value">₹{emi:,.0f}</div>
    </div>
    """
    st.markdown(hero_html, unsafe_allow_html=True)

def render_trust_badge(score: int):
    if score >= 750:
        badge_class = "trust-good"
        emoji = "✅"
        label = "Excellent"
    elif score >= 650:
        badge_class = "trust-fair"
        emoji = "⚠️"
        label = "Good"
    else:
        badge_class = "trust-poor"
        emoji = "❌"
        label = "Needs Improvement"
    
    badge_html = f'<span class="trust-badge {badge_class}">{emoji} {label} Credit</span>'
    st.markdown(badge_html, unsafe_allow_html=True)

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================


def initialize_session_state():
    """Initialize all session state variables."""
    
    # Theme Preference
    if 'theme' not in st.session_state:
        st.session_state.theme = "dark"  # Default theme
    
    # Conversation State
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    if 'maya_chat' not in st.session_state:
        st.session_state.maya_chat = None
    
    if 'master_agent' not in st.session_state:
        st.session_state.master_agent = None
    
    # User Context
    if 'phone' not in st.session_state:
        st.session_state.phone = None
    
    if 'user_data' not in st.session_state:
        st.session_state.user_data = None
    
    if 'verified' not in st.session_state:
        st.session_state.verified = False
    
    if 'consent_given' not in st.session_state:
        st.session_state.consent_given = False
    
    # Loan Parameters
    if 'loan_amount' not in st.session_state:
        st.session_state.loan_amount = 100000
    
    if 'tenure_months' not in st.session_state:
        st.session_state.tenure_months = 36
    
    if 'approved_amount' not in st.session_state:
        st.session_state.approved_amount = None
    
    if 'interest_rate' not in st.session_state:
        st.session_state.interest_rate = None
    
    if 'emi' not in st.session_state:
        st.session_state.emi = None
    
    # Workflow State
    if 'phase' not in st.session_state:
        st.session_state.phase = ConversationPhase.PHASE_1_WARM_OPENING
    
    if 'sanction_pdf_path' not in st.session_state:
        st.session_state.sanction_pdf_path = None
    
    # UI State
    if 'slider_changed' not in st.session_state:
        st.session_state.slider_changed = False
    
    if 'phone_buffer' not in st.session_state:
        st.session_state.phone_buffer = None
    
    # Developer / Demo Mode
    if 'demo_mode' not in st.session_state:
        st.session_state.demo_mode = False
    
    if 'demo_scenario' not in st.session_state:
        st.session_state.demo_scenario = None  # 'ravi', 'priya', or 'sneha'
    
    if 'demo_step' not in st.session_state:
        st.session_state.demo_step = 0
    
    if 'show_sanction_modal' not in st.session_state:
        st.session_state.show_sanction_modal = False
    
    # ========================================================================
    # CONVERSATIONAL PHASE SYSTEM STATE
    # ========================================================================
    
    # Current phase in the 7-phase consultative flow
    if 'conversation_phase' not in st.session_state:
        st.session_state.conversation_phase = ConversationPhase.PHASE_1_WARM_OPENING
    
    # Loan purpose (wedding, education, medical, etc.)
    if 'loan_purpose' not in st.session_state:
        st.session_state.loan_purpose = None
    
    # Requested amount (from user input in Phase 4)
    if 'requested_amount' not in st.session_state:
        st.session_state.requested_amount = None
    
    # Goldilocks 3 options (generated in Phase 4, presented in Phase 5)
    if 'goldilocks_options' not in st.session_state:
        st.session_state.goldilocks_options = None
    
    # Chosen option from Goldilocks (set in Phase 5)
    if 'chosen_option' not in st.session_state:
        st.session_state.chosen_option = None

    # Salary slip confirmation pending (user uploaded suspicious-filename document)
    if 'awaiting_slip_confirm' not in st.session_state:
        st.session_state.awaiting_slip_confirm = False

    # Dynamic key for salary slip uploader — increment to force widget reset after rejection
    if 'slip_uploader_key' not in st.session_state:
        st.session_state.slip_uploader_key = 0

    # Negotiator Agent state — tracks active negotiation and escalation
    if 'negotiation_attempts' not in st.session_state:
        st.session_state.negotiation_attempts = 0
    if 'negotiation_active' not in st.session_state:
        st.session_state.negotiation_active = False
    if 'human_handoff' not in st.session_state:
        st.session_state.human_handoff = False
    # Domain being negotiated ('RATE', 'AMOUNT', 'EMI') — persists across turns
    # so re-fires stay on the same escalation ladder.
    if 'negotiation_domain' not in st.session_state:
        st.session_state.negotiation_domain = None
    
    # Human handoff logic
    if 'refusal_count' not in st.session_state:
        st.session_state.refusal_count = 0
    
    if 'awaiting_handoff' not in st.session_state:
        st.session_state.awaiting_handoff = False
    
    # Name-mismatch pending state — initialized here so Reset clears it correctly
    if 'name_mismatch_pending' not in st.session_state:
        st.session_state.name_mismatch_pending = None

    # Tracks the selected repayment tenure (months) for the live EMI calculator
    if 'selected_tenure' not in st.session_state:
        st.session_state.selected_tenure = 36

    # Salary slip upload simulation for CONDITIONAL approval path
    if 'awaiting_salary_slip' not in st.session_state:
        st.session_state.awaiting_salary_slip = False

    if 'salary_slip_verified' not in st.session_state:
        st.session_state.salary_slip_verified = False


# ============================================================================
# SIDEBAR - TRAFFIC SOURCE & USER PERSONA SIMULATOR
# ============================================================================

def render_sidebar():
    """Render sidebar with reference UI design - avatar card, trust score, selectors."""
    
    with st.sidebar:
        # === THEME TOGGLE ===
        st.markdown("### 🎨 Theme")
        theme_option = st.radio(
            "Choose your theme:",
            options=["🌙 Dark Mode", "☀️ Light Mode"],
            index=0 if st.session_state.theme == "dark" else 1,
            horizontal=True,
            label_visibility="collapsed"
        )
        
        # Update theme if changed
        new_theme = "dark" if "Dark" in theme_option else "light"
        if new_theme != st.session_state.theme:
            st.session_state.theme = new_theme
            st.rerun()
        
        st.markdown("---")
        
        # User Avatar Card (if user loaded)
        if st.session_state.user_data:
            user_name = st.session_state.user_data.get('name', 'Guest User')
            score = st.session_state.user_data.get('score', 750)
            
            # Determine trust label
            if score >= 750:
                trust_label = "Good"
                trust_emoji = "👍"
            elif score >= 650:
                trust_label = "Fair"
                trust_emoji = "👌"
            else:
                trust_label = "Improving"
                trust_emoji = "📈"
            
            st.markdown(f"""
            <div class="avatar-card">
                <div class="avatar-img"></div>
                <div class="avatar-name">{user_name}</div>
                <div class="trust-score-badge">{trust_emoji} CIBIL Score: {score} / 900</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Placeholder when no user selected
            st.markdown("""
<div class="avatar-card">
    <div class="avatar-img"></div>
    <div class="avatar-name">Guest User</div>
    <div class="trust-score-badge">👤 Select Persona</div>
</div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # ── Reset Button (always visible) ────────────────────────────────────
        if st.button("🔄 Reset Conversation", use_container_width=True, type="primary"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
        
        st.markdown("---")
        
        # ── Developer Options toggle (hidden from judges by default) ──────────
        if 'dev_mode' not in st.session_state:
            st.session_state.dev_mode = False
        
        dev_label = "🔧 Dev Options ▲" if st.session_state.dev_mode else "🔧 Dev Options ▼"
        if st.button(dev_label, use_container_width=True):
            st.session_state.dev_mode = not st.session_state.dev_mode
            st.rerun()
        
        # Only render dev widgets when explicitly turned on
        if st.session_state.get('dev_mode', False):
            
            st.markdown("**Traffic Source**")
            traffic_sources = [
                "Direct Visit",
                "📧 Email: Wedding Loan",
                "📱 Ad: Pre-Approved Offer",
                "📧 Email: Home Renovation",
                "📱 Ad: Medical Emergency"
            ]
            selected_traffic = st.selectbox(
                "Select Campaign Source",
                traffic_sources,
                key="traffic_source",
                label_visibility="collapsed"
            )
            
            st.markdown("**Loan Purpose**")
            loan_purposes = {
                "💍 Wedding": "wedding",
                "🏠 Home Renovation": "home",
                "🚗 Vehicle": "vehicle",
                "📚 Education": "education",
                "🏥 Medical": "medical",
                "💼 Business": "business"
            }
            selected_purpose = st.selectbox(
                "Select purpose",
                list(loan_purposes.keys()),
                key="loan_purpose",
                label_visibility="collapsed"
            )
            
            st.markdown("**Quick Test Personas**")
            personas = {
                "-- Select Persona --": "",
                "Ravi Kumar (Score: 780, Limit: 5L)": "9876543210",
                "Priya Sharma (Score: 742, Limit: 6L)": "8765432109",
                "Sneha Patel (Score: 695, Limit: 3L)": "7654321098",
                "Amit Verma (Score: 650, Limit: 4L)": "9812345678",
                "Vikram Desai (Score: 795, Limit: 8L)": "9367890123",
                "Pooja Agarwal (Score: 705, Limit: 2L)": "9278901234"
            }
            selected_persona = st.selectbox(
                "Quick Test Personas",
                list(personas.keys()),
                key="persona_selector",
                label_visibility="collapsed"
            )
            if selected_persona != "-- Select Persona --":
                phone_num = personas[selected_persona]
                st.session_state.phone_buffer = phone_num
                if st.session_state.phone != phone_num:
                    st.session_state.phone = phone_num
                    st.session_state.user_data = get_user(phone_num)
                    st.session_state.verified = True
                    st.session_state.consent_given = True
                    if st.session_state.user_data:
                        st.success(f"📱 Loaded: {st.session_state.user_data['name']}")
                    if st.session_state.master_agent is None:
                        st.session_state.master_agent = MasterAgent(
                            traffic_source=st.session_state.get('traffic_source', 'Direct Visit')
                        )
                st.session_state.master_agent.phase = ConversationPhase.PHASE_3_VERIFICATION
                st.session_state.phase = ConversationPhase.PHASE_3_VERIFICATION
            
            st.markdown("---")
        else:
            # Dev mode OFF — still need defaults for traffic_source and loan_purpose
            # so other parts of the app don't break when accessing session state
            if 'traffic_source' not in st.session_state:
                st.session_state.traffic_source = "Direct Visit"
            if 'loan_purpose' not in st.session_state:
                st.session_state.loan_purpose = "💍 Wedding"
            if 'template_mode' not in st.session_state:
                st.session_state.template_mode = False






# ============================================================================
# AGENT VISUALIZATION
# ============================================================================

def show_agent_workflow(agent_type: str, context: Dict = None):
    """Display agent workflow with st.status."""
    
    workflows = {
        "verification": [
            ("⚙️ Master Agent: Routing to Verification...", 0.5),
            ("🔍 Verification Agent: Connecting to Mock CRM Server...", 0.8),
            ("📡 Fetching user data from database...", 0.6),
            ("✅ Identity Verified: Name & Address Match", 0.4)
        ],
        "underwriting": [
            ("⚙️ Master Agent: Handover to Risk Engine...", 0.4),
            ("📡 Underwriting Agent: Fetching Credit Bureau API...", 0.7),
            ("🔍 Checking Offer Mart Server for limits...", 0.6),
            ("📊 Decision Engine: Running DTI & Risk Models...", 0.8),
            ("✅ Eligibility Check Complete", 0.3)
        ],
        "sanction": [
            ("📄 Sanction Agent: Preparing loan documents...", 0.5),
            ("🔐 Generating Key Fact Statement (KFS)...", 0.6),
            ("📝 Calculating APR and Terms...", 0.5),
            ("✅ PDF Sanction Letter Generated", 0.4)
        ]
    }
    
    if agent_type in workflows:
        with st.status(f"🔄 Agentic Workflow Running...", expanded=True) as status:
            for step_msg, sleep_time in workflows[agent_type]:
                st.write(step_msg)
                time.sleep(sleep_time)
            status.update(label="✅ Workflow Complete", state="complete")

# ============================================================================
# CHAT INTERFACE
# ============================================================================

def md_to_html(text: str) -> str:
    """Convert basic markdown to HTML for chat bubbles."""
    import re
    # Escape HTML special chars first (except we want to keep our own tags)
    text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    # **bold**
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    # *italic*
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
    # `code`
    text = re.sub(r'`(.+?)`', r'<code style="background:rgba(255,255,255,0.1);padding:1px 4px;border-radius:3px;">\1</code>', text)
    # Line breaks
    text = text.replace('\n', '<br>')
    return text


def render_chat_bubble(role, content, avatar, is_typing=False):
    """Render a single chat bubble with HTML. Markdown is converted before embedding."""
    
    # CSS classes
    css_class = "assistant" if role == "assistant" else "user"
    header = "MAYA AI" if role == "assistant" else "YOU"
    
    # Typing specific styles
    if is_typing:
        css_class += " typing"
        content_style = 'style="font-style: italic; color: #94A3B8 !important;"'
        opacity_style = 'style="opacity: 0.7;"'
    else:
        content_style = ''
        opacity_style = ''
        
    # Clean up avatar SVG (remove newlines and extra spaces)
    clean_avatar = " ".join(avatar.split())
    
    # Convert markdown to HTML so **bold** renders correctly
    rendered_content = md_to_html(content) if not is_typing else content
    
    # Build HTML
    html = f"""
<div class="msg-row {css_class}" {opacity_style}>
    <div class="avatar-3d">{clean_avatar}</div>
    <div class="msg-bubble">
        <div class="msg-header">{header}</div>
        <div class="msg-content" {content_style}>{rendered_content}</div>
    </div>
</div>
    """
    
    st.markdown(html, unsafe_allow_html=True)

def display_chat_messages():
    """Display all chat messages using Bliss Mode HTML/CSS."""
    
    for msg in st.session_state.messages:
        role = msg['role']
        content = msg['content']
        
        if role == 'assistant':
            avatar = MAYA_AVATAR
        else:
            avatar = USER_AVATAR
            
        render_chat_bubble(role, content, avatar)

    # Auto-scroll to latest message using a components iframe (same-origin access)
    import streamlit.components.v1 as _components
    _components.html("""
<script>
(function() {
    function scrollChat() {
        try {
            var blocks = window.parent.document.querySelectorAll('[data-testid="stVerticalBlock"]');
            var best = null, bestOverflow = 0;
            blocks.forEach(function(el) {
                var overflow = el.scrollHeight - el.clientHeight;
                if (overflow > bestOverflow) {
                    bestOverflow = overflow;
                    best = el;
                }
            });
            if (best) {
                best.scrollTop = best.scrollHeight;
            }
        } catch(e) {
            // Fallback: try stMain section scroll
            try {
                var main = window.parent.document.querySelector('[data-testid="stMain"]');
                if (main) main.scrollTop = main.scrollHeight;
            } catch(e2) {}
        }
    }
    scrollChat();
    setTimeout(scrollChat, 300);
    setTimeout(scrollChat, 800);
})();
</script>
""", height=0, scrolling=False)



def add_message(role: str, content: str):
    """Add a message to chat history."""
    st.session_state.messages.append({"role": role, "content": content})

import re

def detect_handoff_trigger(user_input: str) -> bool:
    input_lower = user_input.lower()
    handoff_keywords = ["human", "agent", "real person", "customer care", "talk to a person", "executive"]
    return any(k in input_lower for k in handoff_keywords)

def generate_handoff_message() -> str:
    return "I understand you'd like to speak with a human agent. I'm transferring you to our next available customer care executive now. Please hold on for just a moment."

def detect_loan_purpose(user_input: str) -> str:
    input_lower = user_input.lower()
    purpose_map = {
        'wedding': ['wedding', 'shaadi', 'marriage', 'vivah', 'bride', 'groom'],
        'education': ['education', 'college', 'university', 'course', 'degree', 'studies', 'fees', 'school', 'tuition'],
        'medical': ['medical', 'hospital', 'health', 'surgery', 'treatment', 'doctor', 'medicine', 'operation'],
        'home renovation': ['renovation', 'home improvement', 'repair', 'construction', 'interior', 'remodel', 'furnish'],
        'travel': ['travel', 'trip', 'vacation', 'holiday', 'tour', 'abroad'],
        'business': ['business', 'startup', 'shop', 'store', 'enterprise', 'venture'],
        'vehicle': ['car', 'bike', 'vehicle', 'scooter', 'two-wheeler', 'four-wheeler'],
        'personal': ['personal', 'emergency', 'expenses']
    }
    for label, keywords in purpose_map.items():
        if any(kw in input_lower for kw in keywords):
            return label
    return "Not specified"

def extract_tenure_from_input(user_input: str) -> int:
    import re
    input_lower = user_input.lower()
    
    # Check for months (e.g. 40 months, 36m, 40 mo)
    month_match = re.search(r'(\d+)\s*(?:months|month|m|mo)\b', input_lower)
    if month_match:
         return int(month_match.group(1))
         
    # Check for years (e.g. 3 years, 3y, 3 yrs)
    year_match = re.search(r'(\d+)\s*(?:years|year|yr|y|yrs)\b', input_lower)
    if year_match:
         return int(year_match.group(1)) * 12
         
    return 0

def extract_amount_from_input(user_input: str) -> int:
    import re
    input_lower = user_input.lower()
    match = re.search(r'(\d+(?:\.\d+)?)\s*(lakh|lakhs|l\b|k\b|thousand|crore|cr)', input_lower)
    if match:
        num = float(match.group(1))
        unit = match.group(2)
        if unit in ('lakh', 'lakhs', 'l'): return int(num * 100000)
        elif unit in ('k', 'thousand'): return int(num * 1000)
        elif unit in ('crore', 'cr'): return int(num * 10000000)
        else: return int(num)
    digits = re.sub(r'[^\d]', '', user_input)
    if digits: return int(digits)
    return 0

def extract_option_from_input(user_input: str) -> int:
    import re
    input_lower = user_input.lower()
    if re.search(r'\b(1|one|first)\b', input_lower): return 1
    if re.search(r'\b(2|two|second)\b', input_lower): return 2
    if re.search(r'\b(3|three|third)\b', input_lower): return 3
    return 0


# ============================================================================
# 7-PHASE CONVERSATIONAL SYSTEM (Strict Enforced Flow)
# ============================================================================

def handle_phase_1_warm_opening(user_input: str) -> None:
    # Generic greeting, no customer data used initially.
    from app import extract_amount_from_input
    amount = extract_amount_from_input(user_input)
    if amount > 0:
        st.session_state.requested_amount = amount

    import re
    cleaned_input = re.sub(r'[^\w\s]', '', user_input).strip()

    # Loan purpose words must NOT be extracted as names
    purpose_words = {
        "wedding", "education", "travel", "medical", "business",
        "home", "renovation", "house", "studies", "college", "trip",
        "holiday", "emergency", "hospital", "startup", "shop",
    }
    base_words = {
        "i", "am", "my", "name", "is", "need", "a", "an", "loan", "of",
        "for", "lakhs", "rs", "rupees", "lakh", "k", "want", "get",
        "hi", "hello", "hey", "the", "please", "help", "apply"
    } | purpose_words

    input_words = cleaned_input.lower().split()
    remaining_words = [w for w in input_words if w not in base_words and not any(c.isdigit() for c in w)]

    if len(remaining_words) == 0 and not st.session_state.get('user_name'):
        if amount > 0:
            add_message("assistant", f"Got it! You're looking for ✨ **₹{amount:,.0f}**.\n\nTo personalize your experience, **could you please tell me your name?**")
        else:
            add_message("assistant", "I didn't quite catch your name. **Could you please tell me your name?**")
        return # Block transition

    if not st.session_state.get('user_name'):
        # Extract name naively
        name_extracted = " ".join(remaining_words[:2]).title() if remaining_words else user_input.title()
        st.session_state.user_name = name_extracted

    name_str = st.session_state.get('user_name', '')
    greeting = f"Nice to meet you, {name_str}! 👋\n\n" if name_str else "Hello! 👋\n\n"

    # If a shortcut button pre-filled the purpose, skip Phase 2 and go straight to phone verification
    prefilled = st.session_state.pop('prefilled_loan_purpose', None)
    if prefilled:
        st.session_state.loan_purpose = prefilled.title()
        st.session_state.conversation_phase = ConversationPhase.PHASE_3_VERIFICATION
        from conversation_templates import templates
        celebration = templates.celebration_response(prefilled)
        add_message("assistant",
            f"{greeting}{celebration}\n\n"
            f"To calculate your personalized offer and exact interest rate, "
            f"**could you please provide your 10-digit mobile number?** 📱")
    else:
        st.session_state.conversation_phase = ConversationPhase.PHASE_2_PURPOSE_DISCOVERY
        add_message("assistant",
            f"{greeting}I'd be happy to help you with a personal loan today. "
            f"To start, **what is the main purpose of your loan?** "
            f"(e.g. Wedding, Education, Medical, Renovation)")


def handle_phase_2_purpose_discovery(user_input: str) -> None:
    # Extract loan purpose
    from app import detect_loan_purpose, extract_amount_from_input
    
    amount = extract_amount_from_input(user_input)
    if amount > 0:
        st.session_state.requested_amount = amount
        
    purpose = detect_loan_purpose(user_input)
    if not purpose or purpose == "Not specified":
        import re
        cleaned = re.sub(r'[^\w\s]', '', user_input).strip()
        base_words = {"i", "need", "a", "loan", "of", "for", "lakhs", "rs", "rupees", "lakh", "k", "want", "get"}
        input_words = cleaned.lower().split()
        remaining = [w for w in input_words if w not in base_words and not any(c.isdigit() for c in w)]
        
        if len(remaining) == 0:
            if amount > 0:
                add_message("assistant", f"Noted! You need ✨ **₹{amount:,.0f}**.\n\nTo find the right loan, **what is the main purpose?** (e.g. Wedding, Education, Medical, Renovation)")
            else:
                add_message("assistant", "I didn't quite catch the purpose. **Could you tell me what the loan is for?** (e.g. Wedding, Education)")
            return # Block transition
            
        purpose = " ".join(remaining).title()
    
    st.session_state.loan_purpose = purpose
    st.session_state.conversation_phase = ConversationPhase.PHASE_3_VERIFICATION
    
    from conversation_templates import templates
    celebration = templates.celebration_response(purpose)
    
    add_message("assistant", f"{celebration}\n\nTo calculate your personalized offer and exact interest rate, **could you please provide your 10-digit mobile number?** 📱")

def _execute_successful_phase_3(phone: str, user_data: dict) -> None:
    """Helper to execute the money shot once identity is verified."""
    from conversation_templates import templates
    
    st.session_state.phone = phone
    st.session_state.user_data = user_data
    st.session_state.customer_name = user_data['name']
    st.session_state.verified = True
    
    purpose = st.session_state.get('loan_purpose', 'personal needs')
    
    st.session_state.conversation_phase = ConversationPhase.PHASE_4_NEEDS_ANALYSIS
    
    if st.session_state.get('requested_amount'):
        amt = st.session_state.requested_amount
        money_shot = templates.build_profile_presentation(user_data, purpose, ask_amount=False)
        add_message("assistant", f"{money_shot}\n\nSince you already mentioned you need ✨ **₹{amt:,.0f}**, I'm running your affordability check right now! ⚙️")
        from app import handle_phase_4_needs_analysis
        handle_phase_4_needs_analysis(str(amt))
    else:
        money_shot = templates.build_profile_presentation(user_data, purpose, ask_amount=True)
        add_message("assistant", money_shot)

def handle_phase_3_verification(user_input: str) -> None:
    # The Money Shot - and Identity Gate
    from logic import normalize_phone, get_user
    from conversation_templates import templates
    
    # 0. State Interceptor for New Customer Query
    if st.session_state.get('pending_new_customer_query'):
        st.session_state.pending_new_customer_query = False
        user_input_lower = user_input.lower()
        affirmative = ['yes', 'yeah', 'yep', 'true', 'correct', 'i am']
        if any(word in user_input_lower for word in affirmative):
            add_message("assistant", "Ah! This specific AI portal is currently designed to fast-track our **existing pre-approved customers**. If you are a new customer, please visit our main website or nearest branch to apply! Otherwise, if you made a typo, please enter your correct registered 10-digit mobile number.")
        else:
            add_message("assistant", "Got it. Please enter your correct registered 10-digit mobile number.")
        return

    # 1. State Interceptor for pending mismatches
    if st.session_state.get('pending_identity_mismatch'):
        user_input_lower = user_input.lower()
        affirmative = ['yes', 'sure', 'okay', 'ok', 'proceed', 'go ahead', 'yep', 'yeah', 'fine', 'do it', 'accept', 'continue']
        
        if any(word in user_input_lower for word in affirmative):
            # User confirmed the override
            st.session_state.pending_identity_mismatch = False
            user_data = st.session_state.mismatch_user_data
            phone = st.session_state.mismatch_phone
            
            # Adopt the exact registered name
            st.session_state.user_name = user_data['name']
            
            # Proceed with standard Phase 3 success logic
            _execute_successful_phase_3(phone, user_data)
            return
        else:
            # User rejected the override
            st.session_state.pending_identity_mismatch = False
            add_message("assistant", "Okay! To protect your privacy, we won't proceed with that profile. Please provide the correct 10-digit mobile number associated with your application.")
            return

    # 2. Standard flow: parse the new phone number
    phone = normalize_phone(user_input)
    if not phone or len(phone) < 10:
        add_message("assistant", "I couldn't recognize that phone number. Please enter your valid 10-digit mobile number.")
        return
        
    user_data = get_user(phone)
    if not user_data:
        st.session_state.pending_new_customer_query = True
        add_message("assistant", "I couldn't find a pre-approved profile for that number. Are you a new customer? Please ensure you entered the registered number.")
        return
        
    # 3. Mismatch Detection
    provided_name = st.session_state.get('user_name', '').lower()
    registered_name = user_data['name'].lower()
    
    # We do a loose check: if they gave part of their name (e.g., 'Vikram' for 'Vikram Desai'), it's fine.
    # Otherwise, it's a mismatch.
    if provided_name and provided_name not in registered_name and registered_name not in provided_name:
        st.session_state.pending_identity_mismatch = True
        st.session_state.mismatch_user_data = user_data
        st.session_state.mismatch_phone = phone
        
        orig_name = st.session_state.user_name
        add_message("assistant", f"⚠️ **Identity Check**\n\nI noticed you introduced yourself as **{orig_name}**, but the profile registered to this phone number belongs to **{user_data['name']}**.\n\nFor security reasons, please confirm: **Do you want to proceed as {user_data['name']}?**")
        return

    # 4. If logic reaches here, names match or user_name was never captured.
    _execute_successful_phase_3(phone, user_data)

def handle_phase_4_needs_analysis(user_input: str) -> None:
    from app import extract_amount_from_input
    from conversation_templates import templates
    from logic import get_risk_based_rate, calculate_emi, calculate_dti_with_existing_loans, validate_amount_request

    # ── TOP PRIORITY: Path A / B / C selections ──────────────────────────────
    # Handled FIRST, before any state checks, so they always work regardless of
    # session state (awaiting_renegotiation, negotiation_active, etc.)
    if st.session_state.get('user_data'):
        _ui_top = user_input.lower().strip()
        _is_path_a = _ui_top.startswith('path a') or _ui_top == 'a'
        _is_path_b = _ui_top.startswith('path b') or _ui_top == 'b'
        _is_path_c = _ui_top.startswith('path c') or _ui_top == 'c'
        _is_explore = any(p in _ui_top for p in [
            'explore', 'alternative', 'other option', 'other path',
            'different path', 'different option', 'something else',
            'other ways', 'what else', 'what are my options',
        ]) and not any(c.isdigit() for c in _ui_top)

        if _is_path_a or _is_explore:
            _user_data = st.session_state.user_data
            instant_limit = _user_data.get('limit', 0)
            if _is_explore and not _is_path_a:
                # Re-show the full menu
                _score = _user_data.get('score', 700)
                _emis  = _user_data.get('current_emis', 0)
                _path_b_label = "Loan Consolidation" if _emis > 0 else "Improve Your CIBIL Score"
                add_message("assistant",
                    f"Of course! Here are the paths available to you:\n\n"
                    f"**Path A — Start with What's Approved Instantly**\n"
                    f"I can approve up to **₹{instant_limit:,.0f}** right now — no documents needed.\n\n"
                    f"**Path B — {_path_b_label}**\n"
                    f"{'Roll existing EMIs into one product at a lower rate.' if _emis > 0 else f'Your score is {_score}/900 — just {max(700-_score,0)} points from our Standard tier.'}\n\n"
                    f"**Path C — Wait & Strengthen**\n"
                    f"Return in 3–6 months with an improved score for a fast-track approval.\n\n"
                    f"Which path would you like to explore? (Type **'Path A'**, **'Path B'**, or **'Path C'**)")
            else:
                add_message("assistant",
                    f"Great choice! 💪 Let's find an amount that works for you.\n\n"
                    f"Based on your pre-approved profile, I can approve up to "
                    f"**₹{instant_limit:,.0f}** instantly (no salary slip needed).\n\n"
                    f"**How much would you like to borrow?** "
                    f"(e.g. '₹2 lakhs', '150000') and I'll run the check right away.")
            st.session_state.awaiting_renegotiation = True  # ensure next amount goes back here
            return

        if _is_path_b:
            _user_data = st.session_state.user_data
            _current_emis_b = _user_data.get('current_emis', 0)
            _score_b = _user_data.get('score', 700)
            _salary_b = _user_data.get('salary', 0)
            st.session_state.awaiting_renegotiation = False
            if _current_emis_b > 0:
                add_message("assistant",
                    f"Excellent thinking! 🔄 Loan consolidation can simplify your finances "
                    f"and potentially lower your overall EMI.\n\n"
                    f"**Next steps for Loan Consolidation:**\n"
                    f"- Share details of your existing loans (lender, outstanding, EMI)\n"
                    f"- Our team will calculate a consolidated offer within 24 hours\n"
                    f"- Typical savings: 1–3% lower rate + single EMI\n\n"
                    f"📞 Our Senior Relationship Manager **Mr. Arjun Mehta** "
                    f"(+91-22-6789-1234) can arrange this. Shall I initiate the request?")
            else:
                _pts = max(700 - _score_b, 0)
                add_message("assistant",
                    f"Smart move, {_user_data.get('name', '').split()[0]}! 📈 "
                    f"Your current score is **{_score_b}/900** — just **{_pts} points** "
                    f"away from our 700+ Standard tier at 13.5%.\n\n"
                    f"**Your 3-month credit improvement plan:**\n"
                    f"✅ Pay all bills and existing obligations on time\n"
                    f"✅ Keep any credit card balance below 30% of limit\n"
                    f"✅ Avoid applying for new credit during this period\n\n"
                    f"After 3–6 months, you could qualify for up to "
                    f"**₹{int(_salary_b * 0.45 * 29):,.0f}** at 13.5%. "
                    f"Would you like me to set a reminder to recheck your eligibility?")
            return

        if _is_path_c:
            _user_data = st.session_state.user_data
            _score_c = _user_data.get('score', 700)
            st.session_state.awaiting_renegotiation = False
            add_message("assistant",
                f"Absolutely the wisest choice! 🌱 Strengthening your profile first "
                f"means better rates and higher limits.\n\n"
                f"**Your 6-month timeline:**\n"
                f"📅 Month 1–3: Build consistent payment history\n"
                f"📅 Month 3–5: Monitor CIBIL score (target {min(_score_c + 50, 900)}+)\n"
                f"📅 Month 6: Come back to us — we'll fast-track your application "
                f"with updated underwriting.\n\n"
                f"We'll be here whenever you're ready. Best of luck! 🤝")
            return
    # ── End Path A/B/C top-level interceptor ─────────────────────────────────

    # ── Negotiator Interception ───────────────────────────────────────────────
    if st.session_state.get('user_data'):
        from agents.negotiator import NegotiatorAgent
        intent    = NegotiatorAgent.detect_negotiation_intent(user_input)
        is_active = st.session_state.get('negotiation_active', False)


        # ─ Path selection takes absolute priority when negotiation is active.
        # Detect "Path 1/2/3" or synonyms BEFORE the acceptance guard so that
        # digits in e.g. "Path 2" don't accidentally clear negotiation_active.
        if is_active:
            path_sel = NegotiatorAgent.detect_path_selection(user_input)
            if path_sel:
                user_data = st.session_state.user_data
                context_p = {
                    'customer_name' : user_data.get('name', ''),
                    'credit_score'  : user_data.get('score', 750),
                    'rate'          : st.session_state.get('interest_rate') or 13.5,
                    'requested'     : st.session_state.get('requested_amount', 0),
                    'approved'      : st.session_state.get('safe_max_amount',
                                        user_data.get('limit', 0)),
                    'salary'        : user_data.get('salary', 0),
                    'current_emis'  : user_data.get('current_emis', 0),
                    'purpose'       : st.session_state.get('loan_purpose', 'your needs'),
                }
                path_msg, action = NegotiatorAgent.handle_path_selection(path_sel, context_p)
                add_message("assistant", path_msg)

                # Reset negotiation since user accepted an alternative path
                st.session_state.negotiation_active   = False
                st.session_state.negotiation_attempts = 0

                if action == 'SALARY_SLIP':
                    # Trigger salary slip upload — generate goldilocks options and hold
                    from logic import generate_goldilocks_options
                    rate_l   = st.session_state.get('interest_rate') or 13.5
                    amt_l    = context_p['requested']
                    opts     = generate_goldilocks_options(
                        amt_l, rate_l,
                        user_data['salary'], user_data.get('current_emis', 0)
                    )
                    st.session_state.goldilocks_options = opts
                    st.session_state.awaiting_salary_slip    = True
                    st.session_state.conversation_phase = ConversationPhase.PHASE_5_OPTIONS_PRESENTATION

                elif action == 'CO_BORROWER':
                    # Informational — explain process, then keep renegotiation open
                    # so the user's next reply (e.g. 'no I want it all at once') is
                    # captured cleanly instead of falling through to Phase 4.
                    st.session_state.awaiting_renegotiation = True
                    st.session_state.safe_max_amount = context_p['approved']

                elif action == 'SPLIT_LOAN':
                    # Proceed with safe_max immediately — re-run Phase 4 with that amount
                    split_amount = context_p['approved']
                    if split_amount and split_amount >= 10000:
                        from logic import (get_risk_based_rate, calculate_emi,
                                           calculate_dti_with_existing_loans,
                                           generate_goldilocks_options)
                        rate_l   = get_risk_based_rate(user_data['score'])
                        st.session_state.interest_rate    = rate_l
                        st.session_state.requested_amount = split_amount
                        st.session_state.loan_amount      = int(split_amount)
                        opts = generate_goldilocks_options(
                            split_amount, rate_l,
                            user_data['salary'], user_data.get('current_emis', 0)
                        )
                        st.session_state.goldilocks_options = opts
                        st.session_state.conversation_phase = ConversationPhase.PHASE_5_OPTIONS_PRESENTATION

                        from conversation_templates import templates
                        add_message("assistant", templates.build_goldilocks_presentation(opts))

                return   # path handled — stop here
        # ─ End path selection block ──────────────────────────────────────────

        # ─ Acceptance/amount guard: if negotiation was active but user is
        # now accepting or specifying an amount, clear the flag and let the
        # normal flow take over.
        if is_active:
            user_lower_ng = user_input.lower()
            accept_words = [
                'yes', 'ok', 'okay', 'sure', 'fine', 'proceed', 'accept',
                'go ahead', 'continue', 'option', 'let', 'agreed', 'deal',
                'confirm', 'sounds good', 'alright', 'done'
            ]
            has_accept = any(w in user_lower_ng for w in accept_words)
            # Only treat as "has amount" if it's a plausible loan amount (>= ₹10,000)
            amt_check  = extract_amount_from_input(user_input)
            has_amount = bool(amt_check and amt_check >= 10000)
            if has_accept or (has_amount and not intent):
                # User is backing down — close the negotiation loop
                st.session_state.negotiation_active = False
                is_active = False
                # Don't return — let the normal flow below handle it

        # Negotiator firing rules:
        # RATE intent → always fire (user is complaining about rate, always a pushback)
        # AMOUNT intent → only fire if negotiation_active=True (user already went through
        #   validation once and is pushing back). Fresh amount requests must go through
        #   validation first (INSTANT/CONDITIONAL/EXCEED/OVER_CAPACITY).
        # Re-fire (is_active + intent) → still requires live intent to avoid domain bleed.
        _rate_pushback  = (intent == 'RATE' and
                           not st.session_state.get('awaiting_renegotiation_confirmed') and
                           not st.session_state.get('awaiting_renegotiation'))
        _amount_pushback = (intent == 'AMOUNT' and is_active and  # only after first rejection
                            not st.session_state.get('awaiting_renegotiation_confirmed') and
                            not st.session_state.get('awaiting_renegotiation'))
        _refire         = (is_active and intent and
                           not st.session_state.get('awaiting_renegotiation'))
        if _rate_pushback or _amount_pushback or _refire:
            st.session_state.negotiation_active = True
            attempt   = st.session_state.get('negotiation_attempts', 0)
            user_data = st.session_state.user_data

            if attempt >= 3:
                msg = NegotiatorAgent.escalate_to_human(user_data.get('name', 'valued customer'))
                add_message("assistant", msg)
                st.session_state.negotiation_active = False
                st.session_state.human_handoff = True
                return

            context = {
                'customer_name' : user_data.get('name', ''),
                'credit_score'  : user_data.get('score', 750),
                'rate'          : st.session_state.get('interest_rate') or 13.5,
                'requested'     : st.session_state.get('requested_amount', 0),
                'approved'      : st.session_state.get('safe_max_amount',
                                    user_data.get('limit', 0)),
                'salary'        : user_data.get('salary', 0),
                'current_emis'  : user_data.get('current_emis', 0),
                'purpose'       : st.session_state.get('loan_purpose', 'your needs'),
            }
            # Use the live intent when available; otherwise continue the stored domain.
            # Never blindly default to AMOUNT — that causes domain bleed.
            active_intent = intent or st.session_state.get('negotiation_domain') or 'AMOUNT'
            if intent:
                st.session_state.negotiation_domain = intent   # record domain for future re-fires
            msg = NegotiatorAgent.negotiate(active_intent, context, attempt)
            add_message("assistant", msg)
            st.session_state.negotiation_attempts = attempt + 1
            return
    # ── End Negotiator Interception ──────────────────────────────────────────
    
    amount = 0
    if st.session_state.get('awaiting_renegotiation_confirmed'):
        # Rate concern was already answered. Now check what the user actually wants.
        user_lower = user_input.lower()
        affirmative = ['yes', 'sure', 'okay', 'ok', 'proceed', 'go ahead', 'yep', 'yeah', 'fine', 'do it', 'confirm', 'accept']
        explore_keywords = ['explore', 'other', 'different', 'alternatives', 'options', 'lower amount',
                            'something else', 'reconsider', 'change', 'reduce', 'less', 'smaller']

        if any(kw in user_lower for kw in explore_keywords):
            # User wants to explore other amounts — re-enter renegotiation
            st.session_state.awaiting_renegotiation_confirmed = False
            st.session_state.awaiting_renegotiation = True
            locked_amt = st.session_state.get('safe_max_amount', 0)
            add_message("assistant",
                f"Absolutely! Let's explore what works best for you. 😊\n\n"
                f"Our affordability check suggests a maximum of **₹{locked_amt:,.0f}** is comfortable "
                f"given your income and existing commitments.\n\n"
                f"**What amount would you like me to check?** You can say something like "
                f"'₹4 lakhs' or '300000', and I'll run the numbers for you.")
            return   # wait for user's new amount

        elif any(word in user_lower for word in affirmative):
            # User confirmed — run eligibility with the locked counter-offer amount
            amount = st.session_state.get('safe_max_amount', 100000)
            st.session_state.awaiting_renegotiation_confirmed = False

        else:
            # Ambiguous reply — ask for clear confirmation
            locked_amt = st.session_state.get('safe_max_amount', 0)
            add_message("assistant",
                f"Just to clarify — shall I proceed with ✨ **₹{locked_amt:,.0f}**, "
                f"or would you like to explore a different amount?\n\n"
                f"Reply **'yes'** to proceed or tell me an amount you'd prefer.")
            return   # wait for clearer answer

    elif st.session_state.get('awaiting_renegotiation'):
        user_input_lower = user_input.lower()
        affirmative = ['yes', 'sure', 'okay', 'ok', 'proceed', 'go ahead', 'yep', 'yeah', 'fine', 'do it', 'accept']
        rate_keywords = ['rate', 'interest', 'high', 'expensive', 'lower', 'reduce', 'discount', 'less', 'cheaper']

        if any(word in user_input_lower for word in affirmative):
            accepted_amount = st.session_state.get('safe_max_amount', 100000)
            st.session_state.awaiting_renegotiation = False

            # Did the user also raise a rate concern in the same message?
            if any(kw in user_input_lower for kw in rate_keywords):
                # Acknowledge the rate concern first, lock in the amount,
                # and defer the eligibility check to the next reply.
                user_data = st.session_state.user_data
                from logic import get_risk_based_rate
                rate = get_risk_based_rate(user_data['score'])
                from agents.sales import SalesAgent
                rate_reply = SalesAgent.handle_rate_objection(user_data['score'], rate)

                add_message("assistant",
                    f"I've locked in your loan amount at \u2728 **\u20b9{accepted_amount:,.0f}**.\n\n"
                    f"Now, about the interest rate \u2014 let me explain how it\u2019s calculated:\n\n"
                    f"{rate_reply}\n\n"
                    f"Would you like to proceed with this rate, or shall I explore any other options?")

                # Store the locked amount and pause; eligibility runs on the next user turn
                st.session_state.requested_amount = accepted_amount
                st.session_state.loan_amount = int(accepted_amount)
                st.session_state.awaiting_renegotiation_confirmed = True
                return   # stop here; next message triggers the eligibility check
            else:
                amount = accepted_amount
                add_message("assistant", f"Great, I'll update your requested amount to \u2728 **\u20b9{amount:,.0f}**.\n\nLet me recalculate your options...")
        else:
            # ── Path A / B / C selections from the advice card ───────────────
            _ui = user_input.lower().strip()

            # Also catch 'explore alternatives', 'other options', 'alternative path' etc.
            # that appear in negotiator counter-offer responses
            _explore_phrases = [
                'explore', 'alternative', 'other option', 'other path',
                'different path', 'different option', 'something else',
                'other ways', 'what else', 'what are my options',
            ]
            _is_explore = any(p in _ui for p in _explore_phrases)

            if _is_explore or _ui in ('path a', 'a', 'path a.', 'option a') or _ui.startswith('path a'):
                # Use the customer's pre-approved limit for instant approval (not safe_max)
                user_data_pa = st.session_state.get('user_data', {})
                instant_limit = user_data_pa.get('limit', st.session_state.get('safe_max_amount', 0))
                safe_max = st.session_state.get('safe_max_amount', instant_limit)
                if _is_explore and not _ui.startswith('path a'):
                    # Re-show the full path menu
                    add_message("assistant",
                        f"Of course! Here are the paths available to you:\n\n"
                        f"**Path A — Start with What's Approved Instantly**\n"
                        f"I can approve up to **₹{instant_limit:,.0f}** right now — no documents needed. "
                        f"Just type an amount.\n\n"
                        f"**Path B — Improve Your CIBIL Score**\n"
                        f"A few months of consistent payments can push your score past 700 "
                        f"and unlock higher limits.\n\n"
                        f"**Path C — Wait & Strengthen**\n"
                        f"Return in 3–6 months with an improved score for a fast-track approval.\n\n"
                        f"Which path would you like to explore? (Type 'Path A', 'Path B', or 'Path C')")
                else:
                    add_message("assistant",
                        f"Great choice! 💪 Let's find an amount that works for you.\n\n"
                        f"Based on your pre-approved profile, I can approve up to "
                        f"**₹{instant_limit:,.0f}** instantly (no salary slip needed).\n\n"
                        f"**How much would you like to borrow?** "
                        f"(e.g. '₹2 lakhs', '150000') and I'll run the check right away.")
                # Keep awaiting_renegotiation open so the next amount is processed
                return

            if _ui in ('path b', 'b', 'path b.', 'option b') or _ui.startswith('path b'):
                user_data = st.session_state.user_data
                current_emis_b = user_data.get('current_emis', 0)
                score_b = user_data.get('score', 700)
                salary_b = user_data.get('salary', 0)
                st.session_state.awaiting_renegotiation = False
                if current_emis_b > 0:
                    add_message("assistant",
                        f"Excellent thinking! 🔄 Loan consolidation can simplify your finances "
                        f"and potentially lower your overall EMI.\n\n"
                        f"**Next steps for Loan Consolidation:**\n"
                        f"- Share details of your existing loans (lender, outstanding, EMI)\n"
                        f"- Our team will calculate a consolidated offer within 24 hours\n"
                        f"- Typical savings: 1–3% lower rate + single EMI\n\n"
                        f"📞 Our Senior Relationship Manager **Mr. Arjun Mehta** "
                        f"(+91-22-6789-1234) can arrange this. Shall I initiate the request?")
                else:
                    add_message("assistant",
                        f"Smart move, {user_data.get('name', '').split()[0]}! 📈 "
                        f"Your current score is **{score_b}/900** — just **{700 - score_b} points** "
                        f"away from our 700+ Standard tier at 13.5%.\n\n"
                        f"**Your 3-month credit improvement plan:**\n"
                        f"✅ Pay all bills and existing obligations on time\n"
                        f"✅ Keep any credit card balance below 30% of limit\n"
                        f"✅ Avoid applying for new credit during this period\n\n"
                        f"After 3–6 months, you could qualify for up to "
                        f"**₹{int(salary_b * 0.45 * 29):,.0f}** at 13.5%. "
                        f"Would you like me to set a reminder to recheck your eligibility?")
                return

            if _ui in ('path c', 'c', 'path c.', 'option c') or _ui.startswith('path c'):
                user_data = st.session_state.user_data
                score_c = user_data.get('score', 700)
                st.session_state.awaiting_renegotiation = False
                add_message("assistant",
                    f"Absolutely the wisest choice! 🌱 Strengthening your profile first "
                    f"means better rates and higher limits.\n\n"
                    f"**Your 6-month timeline:**\n"
                    f"📅 Month 1–3: Build consistent payment history\n"
                    f"📅 Month 3–5: Monitor CIBIL score (target {min(score_c + 50, 900)}+)\n"
                    f"📅 Month 6: Come back to us — we'll fast-track your application "
                    f"with updated underwriting.\n\n"
                    f"We'll be here whenever you're ready. Best of luck! 🤝")
                return
            # ── End Path A/B/C ────────────────────────────────────────────────

            # Check for explicit rejection first before trying to extract an amount
            rejection_words = ['no', 'nope', "don't", 'dont', 'not', 'reject', 'refuse', 'decline', 'disagree']
            if any(rw in user_input_lower for rw in rejection_words) and not any(c.isdigit() for c in user_input):
                # User refused the counter-offer — keep renegotiation open, ask for their preferred amount
                safe_max = st.session_state.get('safe_max_amount', 0)
                add_message("assistant",
                    f"No problem at all! I understand you'd prefer a different amount. 😊\n\n"
                    f"Just to recap — based on your current income and existing commitments, "
                    f"our affordability model suggests a maximum of **₹{safe_max:,.0f}** is safe "
                    f"right now.\n\n"
                    f"**What amount would you like to try?** You can specify any amount "
                    f"(e.g. '₹5 lakhs', '700000') and I'll instantly check if it works for you.")
                # Keep awaiting_renegotiation = True so the next message goes back here
                return
            else:
                # User provided a new preferred amount — extract it.
                # Also handle 'all at once / the full amount / all of it' phrases
                # that mean the user wants the original requested amount.
                _full_phrases = [
                    'all at once', 'all in one', 'all of it', 'the whole',
                    'full amount', 'the full', 'the entire', 'entire amount',
                    'whole thing', 'everything at once', 'lump sum',
                ]
                _wants_full = any(p in user_input.lower() for p in _full_phrases)
                if _wants_full:
                    amount = st.session_state.get('requested_amount', 0)
                else:
                    amount = extract_amount_from_input(user_input)
                safe_max = st.session_state.get('safe_max_amount', 0)

                # If the user is still requesting above the safe maximum,
                # route to the Negotiator instead of re-running the same
                # rejected affordability check (which would produce an
                # identical rejection — an unhelpful loop).
                if amount and safe_max and amount > safe_max:
                    from agents.negotiator import NegotiatorAgent
                    user_data = st.session_state.user_data
                    attempt   = st.session_state.get('negotiation_attempts', 0)
                    st.session_state.negotiation_active = True
                    st.session_state.awaiting_renegotiation = False  # close the renegotiation loop

                    if attempt >= 3:
                        msg = NegotiatorAgent.escalate_to_human(user_data.get('name', 'valued customer'))
                        add_message("assistant", msg)
                        st.session_state.negotiation_active = False
                        st.session_state.human_handoff = True
                    else:
                        context = {
                            'customer_name' : user_data.get('name', ''),
                            'credit_score'  : user_data.get('score', 750),
                            'rate'          : st.session_state.get('interest_rate') or 13.5,
                            'requested'     : amount,
                            'approved'      : safe_max,
                            'salary'        : user_data.get('salary', 0),
                            'current_emis'  : user_data.get('current_emis', 0),
                            'purpose'       : st.session_state.get('loan_purpose', 'your needs'),
                        }
                        msg = NegotiatorAgent.negotiate('AMOUNT', context, attempt)
                        add_message("assistant", msg)
                        st.session_state.negotiation_attempts = attempt + 1
                    return

                st.session_state.awaiting_renegotiation = False
    else:
        amount = extract_amount_from_input(user_input)

    if not amount or amount < 10000:
        add_message("assistant", "I didn't quite catch the amount. Could you specify it like '5 lakhs' or '500000'?")
        return
        
    st.session_state.requested_amount = amount
    st.session_state.loan_amount = int(amount)
    user_data = st.session_state.user_data
    purpose = st.session_state.get('loan_purpose', 'personal needs')
    
    validation_res = validate_amount_request(user_data, amount)

    # Track approval type for the sanction letter
    st.session_state.loan_type = validation_res['status']  # 'INSTANT_APPROVE' or 'CONDITIONAL'

    rate = get_risk_based_rate(user_data['score'])
    st.session_state.interest_rate = rate
    
    proposed_emi = calculate_emi(amount, 36, rate)
    dti_res = calculate_dti_with_existing_loans(user_data['salary'], proposed_emi, user_data.get('current_emis', 0))
    
    response_msg = templates.build_needs_analysis_response(
        user_data, amount, purpose, validation_res, 
        dti_res['proposed_emi'], dti_res['total_emi'], 
        dti_res['dti'], dti_res['safe']
    )
    
    add_message("assistant", response_msg)
    
    if validation_res['status'] == 'CONDITIONAL':
        # Amount is between 1× and 2× pre-approved limit.
        # Challenge requirement: "request a salary slip upload. Approve only if expected EMI ≤ 50% of salary."
        st.session_state.awaiting_salary_slip = True
        st.session_state.conversation_phase = ConversationPhase.PHASE_5_OPTIONS_PRESENTATION
        st.session_state.negotiation_active  = False   # Phase 4 negotiation ends here
        # Options are prepared but held — released after salary slip is verified
        from logic import generate_goldilocks_options
        opts = generate_goldilocks_options(amount, rate, user_data['salary'], user_data.get('current_emis', 0))
        st.session_state.goldilocks_options = opts
        add_message("assistant", f"""⚠️ **Salary Verification Required**

Your requested amount of **₹{amount:,.0f}** exceeds your instant pre-approved limit of **₹{user_data['limit']:,.0f}**.

As per our lending policy, amounts above the pre-approved limit require **salary verification**.

📎 **Please upload your latest salary slip** (PDF, JPG, or PNG) using the upload button below.

Once verified, I'll confirm your eligibility and present your EMI options!""")
    elif dti_res['safe'] or validation_res['status'] == 'INSTANT_APPROVE':
        st.session_state.conversation_phase   = ConversationPhase.PHASE_5_OPTIONS_PRESENTATION
        st.session_state.negotiation_active   = False   # Phase 4 negotiation ends here
        # Provide the options immediately
        from logic import generate_goldilocks_options
        opts = generate_goldilocks_options(amount, rate, user_data['salary'], user_data.get('current_emis', 0))
        st.session_state.goldilocks_options = opts
        
        options_msg = templates.build_goldilocks_presentation(opts)
        add_message("assistant", options_msg)
    else:
        # User is rejected/over capacity; keep them in Phase 4 to renegotiate amount
        st.session_state.awaiting_renegotiation = True
        st.session_state.safe_max_amount = validation_res.get('alternative_amount', 0)


def handle_phase_5_options_presentation(user_input: str) -> None:
    # Options Presentation (The Goldilocks Rule)
    from app import extract_option_from_input
    from conversation_templates import templates

    # ── Slip confirmation gate (suspicious filename was flagged) ─────────────
    # When awaiting_slip_confirm is True the user saw a soft warning about the
    # uploaded file not looking like a salary slip. They can type 'confirm' to
    # override and proceed, or anything else to re-upload.
    if st.session_state.get('awaiting_slip_confirm'):
        user_lower = user_input.lower()
        affirm = ['confirm', 'yes', 'correct', 'proceed', 'yep', 'yeah', 'sure', 'ok', 'okay', 'it is', "that's right"]

        if any(kw in user_lower for kw in affirm):
            # User confirmed the document override — run underwriting now
            st.session_state.awaiting_slip_confirm    = False
            st.session_state.salary_slip_verified     = True
            st.session_state.awaiting_salary_slip     = False

            from agents.underwriting import UnderwritingAgent
            from logic import calculate_dti_with_existing_loans, calculate_emi
            import time

            user_data    = st.session_state.user_data
            salary       = user_data.get('salary', 50000)
            amount       = st.session_state.requested_amount
            rate         = st.session_state.interest_rate
            current_emis = user_data.get('current_emis', 0)

            add_message("assistant", "Understood — treating the uploaded document as your salary slip. Running underwriting now...")

            with st.session_state.get('_placeholder', st.empty()) if False else (__import__('contextlib').suppress()):
                pass

            decision = UnderwritingAgent.evaluate(user_data['phone'], amount, monthly_salary=salary)

            if decision['status'] == 'APPROVE':
                dti_check = calculate_dti_with_existing_loans(salary, calculate_emi(amount, 36, rate), current_emis)
                add_message("assistant", f"""✅ **Salary Slip Verified!**

📊 **Underwriting Decision**
- Credit Score: **{user_data['score']} / 900** ✅
- Monthly Salary: **₹{salary:,}**
- Existing EMIs: **₹{current_emis:,}**
- Max DTI Capacity: **50% (₹{salary * 0.5:,.0f})**
- New Loan EMI: **₹{calculate_emi(amount, 36, rate):,}**

Your Debt-to-Income ratio is **{dti_check['dti']}%** — within the safe limit! 🎉

Here are your **3 EMI options**:""")
                opts = st.session_state.goldilocks_options
                add_message("assistant", templates.build_goldilocks_presentation(opts))
            else:
                add_message("assistant", f"""❌ **Salary Verification Failed**

Based on your verified income of ₹{salary:,}/month and existing obligations of ₹{current_emis:,}/month, the requested EMI would exceed our **50% DTI limit**.

{decision.get('reason', 'Please consider a lower loan amount.')}

Would you like me to calculate the maximum amount you're eligible for?""")
            return
        else:
            # User wants to re-upload — reset the slip states
            st.session_state.awaiting_slip_confirm = False
            st.session_state.awaiting_salary_slip  = True
            st.session_state.salary_slip_verified  = False
            add_message("assistant",
                "No problem! Please use the **📎 Upload Salary Slip** button below to upload your correct salary slip. "
                "The filename should ideally contain words like 'salary', 'payslip', or 'income' so our system can recognise it.")
            return
    # ── End slip confirmation gate ────────────────────────────────────────────

    # ── Negotiator Interception (Phase 5 — EMI / Rate pushback) ─────────────
    # Fires ONLY on fresh negotiation intent — not on is_active bleed from
    # Phase 4. Option-selection messages ('Option 1', 'go with 2', etc.) are
    # guarded to prevent false positives.
    # Not triggered during salary-slip or document-confirm waits.
    if (st.session_state.get('user_data') and
            not st.session_state.get('awaiting_salary_slip') and
            not st.session_state.get('awaiting_slip_confirm')):
        from agents.negotiator import NegotiatorAgent
        import re as _re
        intent = NegotiatorAgent.detect_negotiation_intent(user_input)

        # Guard: skip if message is clearly an option selection
        # e.g. "Option 1", "option2", "choose 3", "go with option 2"
        is_option_pick = bool(_re.search(r'\b(option\s*[123]|choose\s*[123]|go\s*with\s*[123]|pick\s*[123]|select\s*[123])\b',
                                         user_input.lower()))

        if intent and not is_option_pick:
            st.session_state.negotiation_active = True
            attempt   = st.session_state.get('negotiation_attempts', 0)
            user_data = st.session_state.user_data
            opts      = st.session_state.get('goldilocks_options') or {}
            sel_plan  = opts.get('balanced', {})

            if attempt >= 3:
                msg = NegotiatorAgent.escalate_to_human(user_data.get('name', 'valued customer'))
                add_message("assistant", msg)
                st.session_state.negotiation_active = False
                st.session_state.human_handoff = True
                return

            context = {
                'customer_name' : user_data.get('name', ''),
                'credit_score'  : user_data.get('score', 750),
                'rate'          : st.session_state.get('interest_rate') or 13.5,
                'requested'     : st.session_state.get('requested_amount', 0),
                'approved'      : st.session_state.get('requested_amount', 0),
                'salary'        : user_data.get('salary', 0),
                'current_emis'  : user_data.get('current_emis', 0),
                'emi'           : sel_plan.get('emi', 0),
                'tenure'        : sel_plan.get('tenure', 36),
                'purpose'       : st.session_state.get('loan_purpose', 'your needs'),
            }
            # Phase 5 primarily deals with EMI/rate; fall back to EMI if ambiguous
            active_intent = intent if intent in ('RATE', 'EMI') else 'EMI'
            msg = NegotiatorAgent.negotiate(active_intent, context, attempt)
            add_message("assistant", msg)
            st.session_state.negotiation_attempts = attempt + 1
            return
    # ── End Phase 5 Negotiator Interception ──────────────────────────────────

    # ── Salary-slip waiting state guard ─────────────────────────────────────
    # When awaiting_salary_slip is True the user hasn't uploaded yet.
    # Phase 5 only routes option-selection; general chat would get the
    # generic "I didn't catch" fallback which feels broken. Handle it here.
    if st.session_state.get('awaiting_salary_slip') and not st.session_state.get('salary_slip_verified'):
        user_lower = user_input.lower()
        rate_keywords = ['rate', 'interest', 'high', 'expensive', 'lower', 'reduce', 'discount', 'less', 'cheaper']

        if any(kw in user_lower for kw in rate_keywords):
            # Explain the rate transparently, then redirect to the upload
            user_data = st.session_state.user_data
            from logic import get_risk_based_rate
            rate = get_risk_based_rate(user_data['score'])
            from agents.sales import SalesAgent
            rate_reply = SalesAgent.handle_rate_objection(user_data['score'], rate)
            add_message("assistant",
                f"{rate_reply}\n\n"
                "Once you upload your salary slip below, I'll confirm your eligibility and we can lock in your loan!")
        else:
            # General question / anything else while waiting for the upload
            add_message("assistant",
                "I'm waiting for your salary slip upload to confirm the higher loan amount. "
                "Please use the **📎 Upload Salary Slip** button below to complete verification.\n\n"
                "If you have any questions in the meantime, feel free to ask!")
        return
    # ── End salary-slip guard ────────────────────────────────────────────────

    choice = extract_option_from_input(user_input)
    if not choice:
        # Check if they asked for a custom tenure instead!
        custom_tenure = extract_tenure_from_input(user_input)
        
        if custom_tenure > 0:
            # Re-evaluate affordability for this specific tenure!
            from logic import calculate_emi, calculate_dti_with_existing_loans
            amount = st.session_state.loan_amount
            rate = st.session_state.interest_rate
            user_data = st.session_state.user_data
            
            proposed_emi = calculate_emi(amount, custom_tenure, rate)
            dti_res = calculate_dti_with_existing_loans(user_data['salary'], proposed_emi, user_data.get('current_emis', 0))
            
            if dti_res['safe']:
                st.session_state.selected_option = "Custom"
                st.session_state.selected_tenure = custom_tenure
                st.session_state.approved_emi = int(proposed_emi)
                st.session_state.total_interest = int((proposed_emi * custom_tenure) - amount)
                
                st.session_state.conversation_phase = ConversationPhase.PHASE_6_CONFIRMATION
                add_message("assistant", f"Absolutely! I've recalculated your plan for a custom **{custom_tenure}-month** tenure.\n\nYour new EMI will be **₹{int(proposed_emi):,}**. This keeps your Debt-to-Income ratio at a safe {dti_res['dti']}%.\n\nShould we lock in this custom plan and generate your Sanction Letter?")
                return
            else:
                from logic import calculate_safe_tenure
                safe_tenure = calculate_safe_tenure(amount, user_data['salary'], user_data.get('current_emis', 0), rate)
                
                if safe_tenure == 0 or safe_tenure > 84:
                    add_message("assistant", f"I checked a {custom_tenure}-month plan, but it pushes your Debt-to-Income ratio to {dti_res['dti']}%, which exceeds our 50% safety limit.\n\nEven with the maximum possible extension, this amount remains unaffordable. Could you consider Option 3 (Extended) instead?")
                else:
                    safe_emi = calculate_emi(amount, safe_tenure, rate)
                    add_message("assistant", f"A {custom_tenure}-month plan pushes your Debt-to-Income ratio to {dti_res['dti']}%, which exceeds our 50% safety limit.\n\nHowever, if we extend the tenure to **{safe_tenure} months**, your EMI will drop to **₹{int(safe_emi):,}**, bringing your DTI into the safe zone.\n\nShall we lock in this {safe_tenure}-month counter-offer, or would you prefer one of the original 3 options?")
                return

        add_message("assistant", "I didn't catch your selection. Please reply with Option 1, Option 2, or Option 3, or specify a custom tenure in months (e.g., '40 months').")
        return
        
    opts = st.session_state.goldilocks_options
    plan_map = {1: 'aggressive', 2: 'balanced', 3: 'relaxed'}
    selected_key = plan_map[choice]
    selected_plan = opts[selected_key]
    
    st.session_state.selected_option = choice
    st.session_state.selected_tenure = selected_plan['tenure']
    st.session_state.approved_emi = selected_plan['emi']
    st.session_state.total_interest = selected_plan['total_interest']
    
    user_data = st.session_state.user_data
    purpose = st.session_state.get('loan_purpose', 'personal needs')
    amount = st.session_state.requested_amount
    
    confirmation_msg = templates.build_confirmation_message(user_data, selected_plan, purpose, amount)
    
    st.session_state.conversation_phase = ConversationPhase.PHASE_6_CONFIRMATION
    add_message("assistant", confirmation_msg)

def handle_phase_6_confirmation(user_input: str) -> None:
    # Confirmation before Sanction
    user_input_lower = user_input.lower()
    affirmative = ['yes', 'confirm', 'proceed', 'approve', 'go ahead', 'sure', 'okay', 'ok', 'yep', 'yeah', 'generate']
    negative = ['no', 'wait', 'stop', 'back', 'cancel', 'change']
    
    if any(k in user_input_lower for k in affirmative):
        from assets.sanction_generator import generate_sanction_letter
        
        st.session_state.conversation_phase = ConversationPhase.PHASE_7_DOCUMENTATION
        add_message("assistant", "🎉 **Fantastic! Generating your official sanction letter...**")
        
        user_data = st.session_state.user_data
        amount = st.session_state.requested_amount
        rate = st.session_state.interest_rate
        tenure = st.session_state.selected_tenure
        emi = st.session_state.get('approved_emi', 0)
        total_interest = st.session_state.get('total_interest', 0)
        total_payment = amount + total_interest
        
        loan_details = {
            'customer_name': user_data['name'],
            'phone': user_data['phone'],
            'address': user_data.get('address', 'Address not provided'),
            'pan': user_data.get('pan', 'PAN not provided'),
            'employment': user_data.get('employment', 'Employment details not provided'),
            'credit_score': user_data.get('score', 'N/A'),
            'amount': amount,
            'rate': rate,
            'tenure': tenure,
            'emi': emi,
            'total_interest': total_interest,
            'total_payment': total_payment,
            # Loan type disclosure for the sanction letter
            'loan_type': st.session_state.get('loan_type', 'INSTANT_APPROVE'),
            'pre_approved_limit': user_data.get('limit', 0),
        }
        
        pdf_bytes = generate_sanction_letter(loan_details)
        st.session_state.sanction_letter_bytes = pdf_bytes
        
        from conversation_templates import templates
        success_msg = templates.sanction_success(st.session_state.requested_amount)
        add_message("assistant", success_msg)
        
    elif any(k in user_input_lower for k in negative):
        st.session_state.conversation_phase = ConversationPhase.PHASE_5_OPTIONS_PRESENTATION
        add_message("assistant", "No worries. Let's look at the options again. Which one works better for you? (Option 1, 2, or 3)")
        from conversation_templates import templates
        options_msg = templates.build_goldilocks_presentation(st.session_state.goldilocks_options)
        add_message("assistant", options_msg)
    else:
        add_message("assistant", "Shall I proceed with your selection and generate the sanction letter? (Yes/No)")

def handle_phase_7_documentation(user_input: str) -> None:
    """Documentation & Post-Approval Q&A"""
    # Provide a helpful, contextual response to any post-approval questions.
    amount = st.session_state.get('requested_amount', 0)
    tenure = st.session_state.get('selected_tenure', 0)
    
    helpful_responses = [
        f"Your loan of **₹{amount:,.0f}** has been approved and the sanction letter is ready to download above! 🎉",
        "For disbursement, our team will contact you within 24-48 hours. Please keep your documents ready.",
        "If you have any further questions, please call us at **1800-123-LOAN** (Mon–Sat, 9 AM–6 PM).",
    ]
    
    user_lower = user_input.lower()
    if any(w in user_lower for w in ['when', 'disburs', 'credit', 'transfer']):
        add_message("assistant", "💸 **Disbursement Timeline:** Funds will be credited to your registered bank account within **24–48 hours** after document verification and loan agreement execution.")
    elif any(w in user_lower for w in ['document', 'doc', 'paper', 'submit', 'need']):
        add_message("assistant", "📋 **Documents Required:** Aadhaar, PAN card, 3 months salary slips, 6 months bank statement, and 2 passport-size photos. Please have these ready for our team.")
    elif any(w in user_lower for w in ['emi', 'payment', 'debit', 'auto']):
        add_message("assistant", f"📅 **EMI Details:** Your fixed monthly EMI will be auto-debited via NACH from your registered bank account on the **1st of each month** for {tenure} months.")
    else:
        add_message("assistant", f"Your loan is approved! 🎉 The sanction letter button is available above. For any further assistance, contact us at **loans@loanverse.ai** or call **1800-123-LOAN**.")

def process_ai_response(user_input):
    if 'conversation_phase' not in st.session_state:
        st.session_state.conversation_phase = ConversationPhase.PHASE_1_WARM_OPENING
        
    import re
    # Handoff extraction
    if st.session_state.conversation_phase != ConversationPhase.PHASE_1_WARM_OPENING:
        if detect_handoff_trigger(user_input):
            handoff_msg = generate_handoff_message()
            add_message("assistant", handoff_msg)
            return

    current_phase = st.session_state.conversation_phase
    phase_value = current_phase.value if hasattr(current_phase, 'value') else current_phase
    
    if phase_value == ConversationPhase.PHASE_1_WARM_OPENING.value:
        handle_phase_1_warm_opening(user_input)
    elif phase_value == ConversationPhase.PHASE_2_PURPOSE_DISCOVERY.value:
        handle_phase_2_purpose_discovery(user_input)
    elif phase_value == ConversationPhase.PHASE_3_VERIFICATION.value:
        handle_phase_3_verification(user_input)
    elif phase_value == ConversationPhase.PHASE_4_NEEDS_ANALYSIS.value:
        handle_phase_4_needs_analysis(user_input)
    elif phase_value == ConversationPhase.PHASE_5_OPTIONS_PRESENTATION.value:
        handle_phase_5_options_presentation(user_input)
    elif phase_value == ConversationPhase.PHASE_6_CONFIRMATION.value:
        handle_phase_6_confirmation(user_input)
    elif phase_value == ConversationPhase.PHASE_7_DOCUMENTATION.value:
        handle_phase_7_documentation(user_input)
    else:
        st.session_state.conversation_phase = ConversationPhase.PHASE_1_WARM_OPENING
        handle_phase_1_warm_opening("")

def perform_underwriting_with_templates():
    """
    Run underwriting check and respond with conversational templates.
    This is the actual eligibility check with rich dialogue.
    """
    if not st.session_state.verified:
        st.markdown("""
        <div class="ekyc-alert">
            <span style="font-size: 20px;">⚠️</span>
            <span>Please complete E-KYC verification first.</span>
        </div>
        """, unsafe_allow_html=True)
        return
    
    if not st.session_state.consent_given:
        st.markdown("""
        <div class="ekyc-alert">
            <span style="font-size: 20px;">⚠️</span>
            <span>Please provide consent to fetch your credit report.</span>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # Show agent workflow
    show_agent_workflow("underwriting")
    
    # Check eligibility
    result = check_eligibility(
        phone=st.session_state.phone,
        requested_amount=st.session_state.loan_amount,
        monthly_salary=st.session_state.user_data.get('salary') if st.session_state.user_data else None
    )
    
    if result['status'] == 'APPROVE':
        st.session_state.approved_amount = result['approved_amount']
        st.session_state.interest_rate = result['interest_rate']
        st.session_state.emi = result['emi']
        if st.session_state.master_agent:
            st.session_state.master_agent.phase = ConversationPhase.PHASE_6_CONFIRMATION
        st.session_state.phase = ConversationPhase.PHASE_6_CONFIRMATION
        
        # Calculate total repayment and interest
        total_repayment = result['emi'] * result['tenure_months']
        total_interest = total_repayment - result['approved_amount']
        
        # Use rich conversation template for approval
        approval_message = templates.instant_approval_offer(
            amount=result['approved_amount'],
            interest_rate=result['interest_rate'],
            emi=result['emi'],
            tenure=result['tenure_months'],
            credit_score=st.session_state.user_data.get('score', 750),
            total_repayment=total_repayment,
            total_interest=total_interest
        )
        
        # Display as Maya's message
        st.markdown(f"""
        <div class="assistant-message">
            <div class="avatar">{MAYA_AVATAR}</div>
            <div class="message-content">
                {approval_message.replace(chr(10), '<br>')}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Display interactive loan details cards
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Approved Amount", f"₹{result['approved_amount']:,}")
        with col2:
            st.metric("Interest Rate", f"{result['interest_rate']}% p.a.")
        with col3:
            st.metric("Monthly EMI", f"₹{result['emi']:,}")
        
        # Add to messages (for chat history)
        add_message("assistant", approval_message)
        
    elif result['status'] == 'CONDITIONAL':
        st.warning(f"⚠️ {result['reason']}")
        add_message("assistant", result['reason'])
        
    else:  # REJECT
        # Use empathetic rejection template
        score = st.session_state.user_data.get('score', 0) if st.session_state.user_data else 0
        rejection_message = templates.rejection_with_empathy(
            reason=result['reason'],
            score=score
        )
        
        # Display as Maya's message
        st.markdown(f"""
        <div class="assistant-message">
            <div class="avatar">{MAYA_AVATAR}</div>
            <div class="message-content">
                {rejection_message.replace(chr(10), '<br>')}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        add_message("assistant", rejection_message)

# ============================================================================
# SANCTION LETTER GENERATION
# ============================================================================

def generate_sanction_pdf():
    """Generate and save sanction letter PDF."""
    
    if not st.session_state.approved_amount:
        return
    
    # Show workflow
    show_agent_workflow("sanction")
    
    from assets.sanction_generator import generate_sanction_letter
    
    # Prepare comprehensive loan details exactly as requested by the professional PDF module
    loan_details = {
        # Customer information
        'customer_name': st.session_state.user_data['name'],
        'phone': st.session_state.user_data['phone'],
        'address': st.session_state.user_data.get('address', 'Address not provided'),
        'pan': st.session_state.user_data.get('pan', 'PAN not provided'),
        'employment': st.session_state.user_data.get('employment', 'Employment details not provided'),
        'credit_score': st.session_state.user_data.get('score', 'N/A'),
        
        # Loan financial details
        'amount': st.session_state.approved_amount,
        'rate': st.session_state.interest_rate,
        'tenure': st.session_state.tenure_months,
        'emi': st.session_state.monthly_emi,
        'total_interest': st.session_state.total_interest,
        'total_payment': st.session_state.total_payment
    }
    
    # Generate PDF bytes in pure memory
    pdf_bytes = generate_sanction_letter(loan_details)
    
    st.session_state.sanction_letter_bytes = pdf_bytes

# ============================================================================
# NAVIGATION BAR
# ============================================================================

def render_navigation():
    """Render premium glassmorphic navigation bar."""
    html = '<div class="nav-container"><div class="nav-content"><div class="nav-brand"><div class="nav-icon-box">✨</div><div class="brand-text">Loan<span>Verse</span> AI</div></div></div></div>'
    st.markdown(html, unsafe_allow_html=True)

# ============================================================================
# EMI CALCULATOR COMPONENT
# ============================================================================

def render_mini_option_card(option_data, option_num, loan_amount, selected=False, recommended=False):
    """Render a compact card with donut chart for one Goldilocks option."""
    import plotly.graph_objects as go
    
    border_color = "#14B8A6" if selected else "#334155"
    bg_color = "#0F2027" if selected else "#1E293B"
    
    recommend_badge = '⭐ <span style="color: #F59E0B;">Recommended</span><br>' if recommended else ''
    selected_badge = '✅ <span style="color: #14B8A6;">Selected</span><br>' if selected else ''
    
    # Calculate values for this option
    total_payment = option_data['emi'] * option_data['tenure']
    total_interest = option_data['total_interest']
    principal = loan_amount
    
    # Create mini donut chart
    fig = go.Figure(data=[go.Pie(
        labels=['Principal', 'Interest'],
        values=[principal, total_interest],
        hole=0.65,
        marker=dict(colors=['#14B8A6', '#F59E0B']),
        textinfo='none',
        hovertemplate='<b>%{label}</b><br>₹%{value:,.0f}<extra></extra>',
        showlegend=False
    )])
    
    fig.update_layout(
        margin=dict(t=0, b=0, l=0, r=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=120,
        annotations=[{
            'text': f'{option_data["tenure"] // 12}y',
            'x': 0.5, 'y': 0.5,
            'font': {'size': 16, 'color': 'white', 'family': 'Inter', 'weight': 700},
            'showarrow': False
        }]
    )
    
    # Render card header
    st.markdown(f"""
<div style="border: 2px solid {border_color}; border-radius: 8px; padding: 12px; background: {bg_color}; margin-bottom: 8px;">
    <div style="font-size: 10px; color: #94A3B8; font-weight: 600;">OPTION {option_num}</div>
    <div style="font-size: 14px; color: white; font-weight: 600; margin-top: 4px;">{option_data['label']}</div>
    <div style="font-size: 11px; margin-top: 2px;">{recommend_badge}{selected_badge}</div>
    """, unsafe_allow_html=True)
    
    # Render donut chart
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False}, key=f"option_{option_num}_chart")
    
    # Render EMI and details
    st.markdown(f"""
    <div style="margin-top: 8px; text-align: center;">
        <div style="font-size: 10px; color: #94A3B8;">Monthly EMI</div>
        <div style="font-size: 18px; color: #14B8A6; font-weight: 700;">₹{option_data['emi']:,.0f}</div>
    </div>
    <div style="margin-top: 8px; font-size: 10px; color: #64748B; text-align: center;">
        📅 {option_data['tenure']} months<br>
        📈 Interest: ₹{total_interest/100000:.2f}L
    </div>
</div>
    """, unsafe_allow_html=True)



def render_options_comparison():
    """Render side-by-side comparison of 3 Goldilocks options with donut charts."""
    options = st.session_state.goldilocks_options
    selected_option = st.session_state.get('selected_option', None)
    loan_amount = st.session_state.get('requested_amount', 100000)
    
    st.markdown("---")
    st.markdown('<div style="color: white; font-size: 14px; font-weight: 600; margin: 16px 0 12px 0;">📊 Your 3 Repayment Options</div>', unsafe_allow_html=True)
    
    # Create 3 columns for side-by-side comparison
    col1, col2, col3 = st.columns(3)
    
    with col1:
        render_mini_option_card(
            options['aggressive'], 
            1,
            loan_amount,
            selected=(selected_option == 1)
        )
    
    with col2:
        render_mini_option_card(
            options['balanced'], 
            2,
            loan_amount,
            selected=(selected_option == 2),
            recommended=True
        )
    
    with col3:
        render_mini_option_card(
            options['relaxed'], 
            3,
            loan_amount,
            selected=(selected_option == 3)
        )


def render_emi_calculator():
    """Render EMI calculator synced with Maya's conversation flow."""
    import plotly.graph_objects as go
    
    # DON'T show calculator before conversation starts (prevents mock data)
    if 'messages' not in st.session_state or len(st.session_state.messages) == 0:
        # Show placeholder instead
        st.markdown("### 💳 Live EMI Calculator")
        st.info("Start a conversation with Maya to see your personalized loan details! 💙")
        return
    
    # Get conversation state
    current_gate = st.session_state.get('conversation_phase', ConversationPhase.PHASE_1_WARM_OPENING)
    gate_value = current_gate.value if hasattr(current_gate, 'value') else current_gate
    
    # FIX 1: Show placeholder until we have real loan details from user
    # Only show real numbers if: (a) user confirmed an amount, OR (b) user is verified
    has_real_amount = bool(st.session_state.get('requested_amount'))
    has_real_profile = bool(st.session_state.get('verified') and st.session_state.get('user_data'))
    
    if not has_real_amount and not has_real_profile:
        # Rich animated placeholder — covers the panel space elegantly
        st.markdown("""
<style>
@keyframes shimmer {
  0%   { background-position: -400px 0; }
  100% { background-position: 400px 0; }
}
@keyframes pulse-ring {
  0%, 100% { transform: scale(1); opacity: 0.7; }
  50%       { transform: scale(1.08); opacity: 1; }
}
.emi-skeleton-row {
  height: 14px; border-radius: 7px; margin: 8px 0;
  background: linear-gradient(90deg, rgba(255,255,255,0.04) 25%, rgba(255,255,255,0.1) 50%, rgba(255,255,255,0.04) 75%);
  background-size: 400px 100%;
  animation: shimmer 1.8s infinite linear;
}
.emi-feature-pill {
  display: inline-block;
  background: rgba(20,184,166,0.12);
  border: 1px solid rgba(20,184,166,0.25);
  color: #14B8A6;
  font-size: 11px;
  font-weight: 600;
  padding: 4px 10px;
  border-radius: 20px;
  margin: 4px 3px;
  letter-spacing: 0.3px;
}
</style>
<div class="emi-card" style="padding: 0; overflow: hidden;">

  <!-- Header gradient strip -->
  <div style="background: linear-gradient(135deg, rgba(20,184,166,0.18) 0%, rgba(59,130,246,0.12) 100%); padding: 20px 24px 16px;">
    <div style="display:flex; align-items:center; gap:12px;">
      <div style="animation: pulse-ring 2.4s ease-in-out infinite; font-size:32px;">📊</div>
      <div>
        <div style="font-size:11px; letter-spacing:1.5px; color:#14B8A6; font-weight:700;">LIVE EMI CALCULATOR</div>
        <div style="font-size:13px; color:#94A3B8; margin-top:2px;">Personalised in real time</div>
      </div>
    </div>
  </div>

  <!-- Skeleton preview rows -->
  <div style="padding: 20px 24px;">
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:18px;">
      <div style="color:#64748B; font-size:11px; text-transform:uppercase; letter-spacing:1px; font-weight:600;">Monthly EMI</div>
      <div style="text-align:right; width:40%;">
        <div class="emi-skeleton-row" style="width:80%;"></div>
        <div class="emi-skeleton-row" style="width:50%;"></div>
      </div>
    </div>
    <div style="border-top: 1px solid rgba(255,255,255,0.05); margin: 12px 0;"></div>
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:14px;">
      <div style="color:#64748B; font-size:11px; text-transform:uppercase; letter-spacing:1px; font-weight:600;">Loan Amount</div>
      <div class="emi-skeleton-row" style="width:35%;"></div>
    </div>
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:14px;">
      <div style="color:#64748B; font-size:11px; text-transform:uppercase; letter-spacing:1px; font-weight:600;">Tenure</div>
      <div class="emi-skeleton-row" style="width:25%;"></div>
    </div>
    <div style="display:flex; justify-content:space-between; align-items:center;">
      <div style="color:#64748B; font-size:11px; text-transform:uppercase; letter-spacing:1px; font-weight:600;">Interest Rate</div>
      <div class="emi-skeleton-row" style="width:20%;"></div>
    </div>
  </div>

  <!-- Feature pills -->
  <div style="padding: 0 24px 16px; text-align:center;">
    <span class="emi-feature-pill">✅ Instant calc</span>
    <span class="emi-feature-pill">✅ 3 tenure options</span>
    <span class="emi-feature-pill">✅ Zero hidden fees</span>
  </div>

  <!-- CTA hint -->
  <div style="background: rgba(20,184,166,0.07); border-top: 1px solid rgba(20,184,166,0.15); padding: 14px 24px; text-align:center;">
    <div style="color:#94A3B8; font-size:12px;">💬 <strong style='color:#14B8A6;'>Chat with Maya</strong> to unlock your personalised EMI →</div>
  </div>

</div>
        """, unsafe_allow_html=True)
        return


    # Dynamic value selection based on gate and conversation state
    # ALWAYS prefer requested_amount from chat over any hardcoded default
    _chat_amount = st.session_state.get('requested_amount')
    
    if gate_value == ConversationPhase.PHASE_1_WARM_OPENING.value:
        # Show credit limit if user identified; otherwise show chat amount or 100K default
        if st.session_state.get('verified') and st.session_state.get('user_data'):
            loan_amount = st.session_state.user_data.get('limit', 100000)
            rate = st.session_state.get('interest_rate', 13.5)
            tenure_months = 36
        else:
            loan_amount = _chat_amount or 100000
            rate = 13.5
            tenure_months = 36
    
    elif gate_value in [ConversationPhase.PHASE_2_PURPOSE_DISCOVERY.value,
                        ConversationPhase.PHASE_4_NEEDS_ANALYSIS.value,
                        ConversationPhase.PHASE_3_VERIFICATION.value]:
        # Show requested amount if specified, otherwise user's limit, otherwise default
        if _chat_amount:
            loan_amount = _chat_amount
        elif st.session_state.get('user_data'):
            loan_amount = st.session_state.user_data.get('limit', 100000)
        else:
            loan_amount = 100000
        
        rate = st.session_state.get('interest_rate') or 13.5
        
        # If Goldilocks options exist, use the RECOMMENDED (balanced) tenure
        if st.session_state.get('goldilocks_options'):
            options = st.session_state.goldilocks_options
            tenure_months = options['balanced']['tenure']
        else:
            tenure_months = 36  # Default until options generated
    
    elif gate_value in [ConversationPhase.PHASE_5_OPTIONS_PRESENTATION.value, 
                       ConversationPhase.PHASE_6_CONFIRMATION.value,
                       ConversationPhase.PHASE_7_DOCUMENTATION.value,
                       ConversationPhase.PHASE_7_DOCUMENTATION.value]:
        # Show SELECTED option
        loan_amount = _chat_amount or 100000
        tenure_months = st.session_state.get('selected_tenure', 36)
        rate = st.session_state.get('interest_rate') or 13.5
    
    else:
        # Fallback — still prefer chat amount over default
        loan_amount = _chat_amount or 100000
        tenure_months = 36
        rate = 13.5

    
    # Calculate EMI (ensure rate is not None)
    if rate is None:
        rate = 13.5  # Default fallback rate
    
    monthly_rate = rate / (12 * 100)
    
    if monthly_rate > 0:
        emi = loan_amount * monthly_rate * (1 + monthly_rate)**tenure_months / ((1 + monthly_rate)**tenure_months - 1)
    else:
        emi = loan_amount / tenure_months
    
    total_payment = emi * tenure_months
    total_interest = total_payment - loan_amount
    
    # Header
    st.markdown('<div class="emi-header" style="margin-top: 20px;">', unsafe_allow_html=True)
    st.markdown('<div class="emi-label">MONTHLY EMI</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="emi-amount">₹{int(emi):,}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Donut Chart
    fig = go.Figure(data=[go.Pie(
        labels=['Principal', 'Interest'],
        values=[loan_amount, total_interest],
        hole=0.7,
        marker=dict(colors=['#14B8A6', '#F59E0B']),
        textinfo='none',
        hovertemplate='<b>%{label}</b><br>₹%{value:,.0f}<extra></extra>'
    )])
    
    fig.update_layout(
        showlegend=False,
        margin=dict(t=0, b=0, l=0, r=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=200,
        annotations=[{
            'text': f'₹{total_payment/100000:.1f}L<br><span style="font-size:12px; opacity:0.85;">Total Payment</span>',
            'x': 0.5, 'y': 0.5,
            'font': {'size': 20, 'family': 'Inter'},
            'showarrow': False
        }]
    )
    
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    # Legend
    st.markdown("""
<div class="emi-legend">
    <div class="legend-item">
        <div class="legend-dot principal"></div>
        <span>Principal</span>
    </div>
    <div class="legend-item">
        <div class="legend-dot interest"></div>
        <span>Interest</span>
    </div>
</div>
    """, unsafe_allow_html=True)
    
    # Info Cards Grid
    st.markdown('<div class="info-cards-grid">', unsafe_allow_html=True)
    
    # Loan Amount Card
    st.markdown(f"""
<div class="info-card">
    <div class="info-card-label">💰 LOAN AMOUNT</div>
    <div class="info-card-value cyan">₹{loan_amount/100000:.1f}L</div>
</div>
    """, unsafe_allow_html=True)
    
    # Tenure Card
    st.markdown(f"""
<div class="info-card">
    <div class="info-card-label">📅 TENURE</div>
    <div class="info-card-value purple">{tenure_months} months</div>
</div>
    """, unsafe_allow_html=True)
    
    # Interest Rate Card
    st.markdown(f"""
<div class="info-card">
    <div class="info-card-label">📊 INTEREST RATE</div>
    <div class="info-card-value yellow">{rate}% p.a.</div>
</div>
    """, unsafe_allow_html=True)
    
    # Total Interest Card
    st.markdown(f"""
<div class="info-card">
    <div class="info-card-label">📈 TOTAL INTEREST</div>
    <div class="info-card-value red">₹{total_interest/100000:.2f}L</div>
</div>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)  # Close info-cards-grid
    
    # ✨ NEW: Show 3 options comparison if in Gates 2B or 3
    if gate_value in [ConversationPhase.PHASE_2_PURPOSE_DISCOVERY.value, ConversationPhase.PHASE_4_NEEDS_ANALYSIS.value, ConversationPhase.PHASE_3_VERIFICATION.value]:
        if st.session_state.get('goldilocks_options'):
            render_options_comparison()


# ============================================================================
# HERO/LANDING SECTION
# ============================================================================

def render_hero_section():
    """Render hero/landing page matching screenshot design."""
    col_left, col_right = st.columns([3, 2])
    
    with col_left:
        # Get dynamic greeting
        greeting = get_dynamic_greeting()
        
        # Hero content
        st.markdown(f"""
<div class="hero-container">
    <div class="hero-greeting">{greeting}</div>
    <h1 class="hero-title">
        Your Dreams,<br>
        <span class="hero-title-gradient">Funded in Minutes.</span>
    </h1>
    <p class="hero-subtitle">
        Meet <strong>Maya</strong> — your AI loan advisor. Tell her your goals, and 
        she'll find the perfect loan for you.
    </p>
</div>
        """, unsafe_allow_html=True)
        
        
        # Talk to Maya button (no input field needed)
        col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
        with col_btn2:
            if st.button("💬 Talk to Maya", use_container_width=True, type="primary", key="start_conversation_btn"):
                # Start conversation by showing Maya's initial greeting
                if 'messages' not in st.session_state or len(st.session_state.messages) == 0:
                    add_message("assistant", "Hello! I'm Maya, your AI relationship manager at LoanVerse. I'd be happy to help you with a personal loan today. 🙂\n\nTo get started, **may I have your name?**")
                st.rerun()
        
        # Quick action pills
        st.markdown('<div class="quick-actions">', unsafe_allow_html=True)
        quick_actions = [
            ("Wedding 💒",       "wedding"),
            ("Education 📚",     "education"),
            ("Travel ✈️",        "travel"),
            ("Home Renovation 🏠", "home renovation"),
            ("Medical 🏥",       "medical"),
            ("Business 💼",      "business"),
        ]

        cols = st.columns(3)
        for idx, (label, purpose) in enumerate(quick_actions):
            with cols[idx % 3]:
                if st.button(label, key=f"qa_{idx}", use_container_width=True):
                    # Ensure Maya's greeting is in chat
                    if 'messages' not in st.session_state or len(st.session_state.messages) == 0:
                        add_message("assistant",
                            "Hello! I'm Maya, your AI relationship manager at LoanVerse. "
                            "I'd be happy to help you with a personal loan today. 🙂\n\n"
                            "To get started, **may I have your name?**")
                    # Pre-fill the loan purpose so Phase 2 skips the purpose question
                    st.session_state.prefilled_loan_purpose = purpose
                    # Show a clean user bubble so the conversation doesn't look blank
                    add_message("user", f"I need a loan for {purpose}")
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col_right:
        # Credit health widget (simplified for now)
        st.markdown("""
<div class="credit-widget">
    <div style="text-align: center; margin-bottom: 16px;">
        <div class="emi-label">MARKET AVG CREDIT HEALTH</div>
        <div class="credit-score">758</div>
        <div class="credit-status">Good — Typical LoanVerse Customer</div>
        <div class="credit-trend">📈 Avg score improved +18 pts in 2025</div>
    </div>
</div>
        """, unsafe_allow_html=True)
        
        # Stats footer
        st.markdown("""
<div class="stats-footer" style="grid-template-columns: repeat(4, 1fr); border-top: none;">
    <div class="stat-item">
        <div class="stat-value cyan">₹120 Cr+</div>
        <div class="stat-label">Loans Disbursed</div>
    </div>
    <div class="stat-item">
        <div class="stat-value gold">5,000+</div>
        <div class="stat-label">Happy Customers</div>
    </div>
    <div class="stat-item">
        <div class="stat-value green">&lt; 3 min</div>
        <div class="stat-label">Avg Decision Time</div>
    </div>
    <div class="stat-item">
        <div class="stat-value purple">91%</div>
        <div class="stat-label">Approval Rate</div>
    </div>
</div>
        """, unsafe_allow_html=True)

# ============================================================================
# CHAT LAYOUT
# ============================================================================

def render_chat_layout():
    """Render main chat + calculator layout."""
    col_chat, col_calculator = st.columns([3, 2])
    
    # ── Chat input styling (theme-aware) ─────────────────────────────────────
    _is_light    = st.session_state.get("theme", "dark") == "light"
    _bg          = "#FFFFFF"                  if _is_light else "#0A1628"
    _bg_focus    = "#F5FFFE"                  if _is_light else "#0B1A2D"
    _text        = "#1E293B"                  if _is_light else "#E2E8F0"
    _ph_color    = "#94A3B8"                  if _is_light else "#3D5470"
    _border      = "1px solid rgba(15, 118, 110, 0.4)" if _is_light else "1px solid rgba(148, 163, 184, 0.4)"
    _glow_start  = "rgba(20,184,166,0.10)"   if _is_light else "rgba(20,184,166,0.18)"
    _shadow_idle = "0 4px 16px rgba(15, 118, 110, 0.15)" if _is_light else "0 4px 16px rgba(0,0,0,0.50)"

    st.markdown(f"""
<style>
/* ── SAFE, VISUALLY APPEALING CHAT INPUT (No structural overrides) ── */

/* 1. Main outer container styling (only colors, borders, shadows, padding) */
div[data-testid="stChatInput"] {{
    background-color: {_bg} !important;
    border: {_border} !important;
    border-radius: 28px !important;
    padding: 0px 4px !important;
    box-shadow: {_shadow_idle} !important;
    transition: all 0.3s ease !important;
}}

/* Focus state */
div[data-testid="stChatInput"]:focus-within {{
    border-color: #14B8A6 !important;
    box-shadow: 0 0 0 2px rgba(20,184,166,0.2) !important;
    background-color: {_bg_focus} !important;
}}

/* 2. Inner backgrounds must be transparent so the pill background shows */
div[data-testid="stChatInput"] div[data-baseweb="textarea"],
div[data-testid="stChatInput"] div[data-baseweb="base-input"],
div[data-testid="stChatInput"] > div,
div[data-testid="stChatInput"] > div > div,
div[data-testid="stChatInput"] > div > div > div,
div[data-testid="stChatInput"] > div > div > div > div {{
    background-color: transparent !important;
    background: transparent !important;
    border: none !important;
}}

/* 3. The editable textarea itself */
textarea[data-testid="stChatInputTextArea"] {{
    background-color: transparent !important;
    color: {_text} !important;
    -webkit-text-fill-color: {_text} !important;
    caret-color: #14B8A6 !important;
    font-size: 15px !important;
    padding: 14px 16px !important;
}}

textarea[data-testid="stChatInputTextArea"]::placeholder {{
    color: {_ph_color} !important;
    font-style: italic !important;
    opacity: 1 !important;
}}

/* 4. The Send Button (Gradient circle) */
button[data-testid="stChatInputSubmitButton"] {{
    background: linear-gradient(140deg, #14B8A6 0%, #06B6D4 60%, #0EA5E9 100%) !important;
    border-radius: 50% !important;
    width: 38px !important;
    height: 38px !important;
    border: none !important;
    box-shadow: 0 2px 8px rgba(20,184,166,0.3) !important;
    margin: 4px 4px 4px 0 !important;
    transition: transform 0.2s ease !important;
}}

button[data-testid="stChatInputSubmitButton"]:hover {{
    transform: scale(1.08) !important;
    box-shadow: 0 4px 12px rgba(20,184,166,0.4) !important;
}}

/* Bulletproof way to make the icon white without accidentally filling bounding boxes */
button[data-testid="stChatInputSubmitButton"] svg {{
    filter: brightness(0) invert(1) !important;
}}
</style>""", unsafe_allow_html=True)
    # ── End chat input styling ────────────────────────────────────────────────





    
    with col_chat:
        st.markdown("### 💬 Chat with Maya")

        
        # Chat container — taller for breathing room
        chat_container = st.container(height=480)
        with chat_container:
            # Show greeting if first time
            if len(st.session_state.messages) == 0:
                if st.session_state.master_agent is None:
                    st.session_state.master_agent = MasterAgent(
                        traffic_source=st.session_state.get('traffic_source', 'Direct Visit')
                    )
                greeting = st.session_state.master_agent.get_contextual_greeting()
                add_message("assistant", greeting)
                if not st.session_state.phone:
                    st.session_state.master_agent.phase = ConversationPhase.PHASE_2_PURPOSE_DISCOVERY
                    st.session_state.phase = ConversationPhase.PHASE_2_PURPOSE_DISCOVERY
                elif not st.session_state.consent_given:
                    st.session_state.master_agent.phase = ConversationPhase.PHASE_3_VERIFICATION
                    st.session_state.phase = ConversationPhase.PHASE_3_VERIFICATION
            
            display_chat_messages()

            # Show Sanction Letter Download Button if generated
            if st.session_state.get('sanction_letter_bytes'):
                pdf_bytes = st.session_state.sanction_letter_bytes
                customer_name = st.session_state.user_data['name'].replace(' ', '_')
                file_name_str = f"LoanVerse_Sanction_Letter_{customer_name}.pdf"
                
                # Write to Downloads folder — 100% reliable for local Streamlit app
                # (browser-based downloads fail in Streamlit's sandboxed iframe)
                downloads_dir = os.path.join(os.path.expanduser("~"), "Downloads")
                save_path = os.path.join(downloads_dir, file_name_str)
                
                if st.button(
                    "📄 Download Official Sanction Letter (PDF)",
                    type="primary",
                    use_container_width=True,
                    key="btn_download_sanction_pdf"
                ):
                    try:
                        os.makedirs(downloads_dir, exist_ok=True)
                        with open(save_path, "wb") as f:
                            f.write(pdf_bytes)
                        os.startfile(save_path)
                        st.success(f"✅ Sanction letter saved and opened! \n📁 Location: `{save_path}`")
                    except Exception as e:
                        st.error(f"Could not save PDF: {e}")

            # Salary Slip Upload Widget — shown for CONDITIONAL approval path
            # (Amount > pre-approved limit but ≤ 2× limit)
            if st.session_state.get('awaiting_salary_slip') and not st.session_state.get('salary_slip_verified'):
                st.markdown("---")
                st.markdown("#### 📎 Upload Salary Slip")
                uploaded_file = st.file_uploader(
                    "Upload your latest salary slip (PDF, JPG, PNG)",
                    type=["pdf", "jpg", "jpeg", "png"],
                    key=f"salary_slip_uploader_{st.session_state.get('slip_uploader_key', 0)}",
                    label_visibility="collapsed"
                )
                if uploaded_file is not None:
                    # ── Step 1: Scanning ──────────────────────────────────────────────────
                    import time
                    with st.spinner("📄 Scanning document..."):
                        time.sleep(0.8)

                    # ── Step 2: Mock CRM Cross-Verification ───────────────────────────────
                    user_data = st.session_state.user_data
                    registered_name  = user_data.get('name', '')
                    registered_phone = user_data.get('phone', '')
                    provided_name    = st.session_state.get('customer_name', '') or st.session_state.get('user_name', '')
                    session_phone    = st.session_state.get('phone', '')

                    # Name match: at least one word of provided name appears in the registered name
                    name_words = provided_name.lower().split()
                    name_ok = any(w in registered_name.lower() for w in name_words) if name_words else True
                    phone_ok = (session_phone == registered_phone)

                    # ── Document-level validation ─────────────────────────────────────────
                    file_bytes    = uploaded_file.getvalue()
                    file_size_kb  = len(file_bytes) / 1024
                    file_name_lc  = uploaded_file.name.lower()
                    file_ext      = file_name_lc.rsplit('.', 1)[-1] if '.' in file_name_lc else ''
                    allowed_exts  = {'pdf', 'jpg', 'jpeg', 'png'}

                    # File size check (2 KB minimum, 20 MB maximum)
                    size_ok  = 2 <= file_size_kb <= 20480
                    size_msg = (
                        f"Size OK — **{file_size_kb:,.1f} KB** ✔"
                        if size_ok else
                        (f"File too small ({file_size_kb:.1f} KB) — may be blank or corrupt"
                         if file_size_kb < 5 else
                         f"File too large ({file_size_kb/1024:.1f} MB) — please compress and re-upload")
                    )

                    # File type check
                    type_ok  = file_ext in allowed_exts
                    type_msg = (
                        f"Accepted format: **{file_ext.upper()}** ✔"
                        if type_ok else
                        f"Unsupported format '.{file_ext}' — please upload PDF, JPG, or PNG"
                    )

                    # Filename keyword analysis — does this look like a salary document?
                    salary_keywords = [
                        'salary', 'payslip', 'pay_slip', 'payroll', 'paystub', 'pay_stub',
                        'income', 'compensation', 'wage', 'earning', 'slip', 'stub', 'ctc',
                        'offer_letter', 'offer letter', 'employment', 'hike', 'remuner'
                    ]
                    # Screenshots / unrelated documents to flag
                    unrelated_flags = [
                        'screenshot', 'photo', 'img_', 'dsc_', 'cam', 'whatsapp',
                        'selfie', 'profile', 'wallpaper', 'meme', 'video', 'thumbnail'
                    ]
                    is_salary_doc = any(kw in file_name_lc for kw in salary_keywords)
                    is_unrelated  = any(fl in file_name_lc for fl in unrelated_flags)

                    # Keyword check result
                    keyword_ok  = is_salary_doc and not is_unrelated
                    keyword_msg_pass = f"Filename '{uploaded_file.name}' matches salary document pattern ✔"
                    keyword_msg_warn = (
                        f"⚠️ Filename '{uploaded_file.name}' doesn't look like a salary slip — please confirm this is the correct document"
                        if not is_salary_doc else
                        f"⚠️ Filename suggests this may not be a financial document — please re-check"
                    )

                    with st.spinner("🔍 Cross-verifying with CRM database..."):
                        time.sleep(1.2)

                    # ── Build verification card ───────────────────────────────────────────
                    checks = [
                        ("Name on document",            name_ok,     f"Matched: **{registered_name}**",          "Could not match — proceeding with registered name"),
                        ("Registered mobile number",    phone_ok,    f"Verified: **{registered_phone}**",         "Session phone mismatch — using CRM record"),
                        ("File type",                   type_ok,     type_msg,                                    type_msg),
                        ("File size",                   size_ok,     size_msg,                                    size_msg),
                        ("Document keyword match",      keyword_ok,  keyword_msg_pass,                            keyword_msg_warn),
                        ("Employment / salary band",    True,        "Salary within declared range ✔",            ""),
                    ]

                    card_lines = ["🔍 **Document Verification Report**\n"]
                    for label, passed, ok_msg, fail_msg in checks:
                        icon = "✅" if passed else "⚠️"
                        msg  = ok_msg if passed else fail_msg
                        card_lines.append(f"{icon} **{label}:** {msg}")

                    # Hard rejection: file too small OR wrong type → stop, ask to re-upload
                    if not size_ok or not type_ok:
                        card_lines.append("\n❌ **Verification Failed — please re-upload a valid salary slip.**")
                        add_message("assistant", "\n".join(card_lines))
                        # Increment uploader key to force widget reset (clears the rejected file)
                        st.session_state.slip_uploader_key = st.session_state.get('slip_uploader_key', 0) + 1
                        st.session_state.salary_slip_verified = False
                        st.session_state.awaiting_salary_slip = True
                        st.rerun()
                        return

                    # Soft warning: document doesn't look like a salary slip by name
                    if not keyword_ok:
                        card_lines.append(
                            "\n⚠️ **The uploaded file doesn't appear to be a salary slip based on its name and properties.**\n"
                            "If you are sure this is the correct document, type **'confirm'** and I'll proceed. "
                            "Otherwise, please re-upload the correct file."
                        )
                        add_message("assistant", "\n".join(card_lines))
                        # Increment key so uploader clears if user decides to re-upload
                        st.session_state.slip_uploader_key = st.session_state.get('slip_uploader_key', 0) + 1
                        st.session_state.awaiting_slip_confirm = True
                        st.session_state.salary_slip_verified  = False
                        st.session_state.awaiting_salary_slip  = False
                        st.rerun()
                        return

                    all_passed = name_ok and phone_ok and size_ok and type_ok and keyword_ok
                    if all_passed:
                        card_lines.append("\n🎯 **All checks passed — proceeding to underwriting.**")
                    else:
                        card_lines.append("\n⚠️ **Minor discrepancies noted but proceeding with CRM record.**")

                    add_message("assistant", "\n".join(card_lines))

                    # ── Step 3: Mark verified and run underwriting ────────────────────────
                    st.session_state.salary_slip_verified = True
                    st.session_state.awaiting_salary_slip = False

                    from agents.underwriting import UnderwritingAgent
                    from logic import calculate_dti_with_existing_loans, calculate_emi

                    salary      = user_data.get('salary', 50000)
                    amount      = st.session_state.requested_amount
                    rate        = st.session_state.interest_rate
                    current_emis = user_data.get('current_emis', 0)

                    with st.spinner("⚙️ Running underwriting engine..."):
                        time.sleep(0.6)

                    decision = UnderwritingAgent.evaluate(
                        user_data['phone'], amount, monthly_salary=salary
                    )

                    if decision['status'] == 'APPROVE':
                        dti_check = calculate_dti_with_existing_loans(salary, calculate_emi(amount, 36, rate), current_emis)
                        add_message("assistant", f"""✅ **Salary Slip Verified!**

📊 **Underwriting Decision**
- Credit Score: **{user_data['score']} / 900** ✅
- Monthly Salary: **₹{salary:,}**
- Existing EMIs: **₹{current_emis:,}**
- Max DTI Capacity: **50% (₹{salary * 0.5:,.0f})**
- New Loan EMI: **₹{calculate_emi(amount, 36, rate):,}**

Your Debt-to-Income ratio is **{dti_check['dti']}%** — within the safe limit! 🎉

Here are your **3 EMI options**:""")
                        from conversation_templates import templates
                        opts = st.session_state.goldilocks_options
                        add_message("assistant", templates.build_goldilocks_presentation(opts))
                    else:
                        add_message("assistant", f"""❌ **Salary Verification Failed**

Based on your verified income of ₹{salary:,}/month and existing obligations of ₹{current_emis:,}/month, the requested EMI would exceed our **50% DTI limit**.

{decision.get('reason', 'Please consider a lower loan amount.')}

Would you like me to calculate the maximum amount you're eligible for?""")
                    st.rerun()

            # Show typing indicator inside chat container (Bliss Mode)
            if st.session_state.messages and st.session_state.messages[-1]['role'] == "user":
                render_chat_bubble("assistant", "Thinking...", MAYA_AVATAR, is_typing=True)
        
        # Chat input
        user_input = st.chat_input("Type your message here...")
        if user_input:
            add_message("user", user_input)
            st.rerun()

        # Process AI response if needed
        if st.session_state.messages and st.session_state.messages[-1]['role'] == "user":
            # Standard AI mode
            process_ai_response(st.session_state.messages[-1]['content'])
            
            st.rerun()
    
    with col_calculator:
        # Render the EMI calculator component
        render_emi_calculator()

# ============================================================================
# MAIN APP
# ============================================================================

def main():
    """Main application entry point."""
    
    # Initialize
    initialize_session_state()
    load_custom_css_file()
    
    # Render navigation bar
    render_navigation()
    
    # Render sidebar (HIDDEN for demo - uncomment if needed)
    render_sidebar()
    
    # Check if we should show hero/landing page or chat interface
    show_hero = len(st.session_state.messages) == 0
    
    if show_hero:
        # Show hero/landing page
        render_hero_section()
    else:
        # Show main chat + calculator layout
        render_chat_layout()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #64748B; padding: 20px; font-size: 0.8rem;">
        LoanVerse AI | Powered by Google Gemini
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
