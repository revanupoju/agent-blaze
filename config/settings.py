"""Central configuration for Apollo Cash AI Marketing Agent."""

# ── Brand Identity ──────────────────────────────────────────────
BRAND = {
    "name": "Apollo Cash",
    "tagline": "Paison ki tension khatam",
    "app_link": "https://play.google.com/store/apps/details?id=com.apollocash",
    "loan_range": "₹5,000 – ₹2,00,000",
    "tenure": "3 / 6 / 9 months",
    "disbursal_time": "15 minutes",
    "interest_note": "Interest rates vary by profile",
    "usp": [
        "No collateral needed",
        "Minimal documentation",
        "Works for NTC (New To Credit) users",
        "No judgement, no drama",
        "Disbursal in 15 minutes",
    ],
}

# ── Target Audience Segments ────────────────────────────────────
AUDIENCE_SEGMENTS = {
    "gig_workers": {
        "label": "Gig Workers",
        "description": "Zomato/Swiggy riders, Uber/Ola drivers, delivery partners",
        "pain_points": [
            "Irregular income",
            "No salary slip for loan eligibility",
            "Bike/phone repair emergencies",
            "Weekly settlements don't align with monthly bills",
        ],
        "language_style": "Very casual Hinglish, bhai-tone, uses slang",
        "platforms": ["instagram", "youtube_shorts", "whatsapp", "sharechat"],
    },
    "salaried_tier2": {
        "label": "Salaried (Tier 2/3)",
        "description": "Earning ₹15K-40K/month in smaller cities",
        "pain_points": [
            "Salary delay by employer",
            "Month-end cash crunch",
            "Festival/wedding expenses",
            "Medical emergencies",
        ],
        "language_style": "Hinglish, relatable office humor, slightly formal",
        "platforms": ["instagram", "facebook", "whatsapp", "youtube"],
    },
    "self_employed": {
        "label": "Self-Employed",
        "description": "Kirana owners, street vendors, auto drivers, tailors",
        "pain_points": [
            "Stock purchase timing",
            "Vehicle repair costs",
            "Seasonal income fluctuation",
            "No bank will give them a loan easily",
        ],
        "language_style": "Hindi-heavy Hinglish, practical tone, story-based",
        "platforms": ["facebook", "whatsapp", "youtube", "sharechat"],
    },
    "ntc_youth": {
        "label": "New To Credit (21-35)",
        "description": "First-time borrowers, no credit history, often anxious about loans",
        "pain_points": [
            "No CIBIL score",
            "Fear of loan sharks / predatory apps",
            "Don't know how EMI works",
            "Embarrassment about borrowing",
        ],
        "language_style": "Gen Z Hinglish, meme-aware, casual and reassuring",
        "platforms": ["instagram", "youtube_shorts", "twitter"],
    },
}

# ── Content Formats ─────────────────────────────────────────────
CONTENT_FORMATS = {
    "instagram_carousel": {
        "slides": "4-6",
        "style": "Story-driven, one idea per slide, strong hook on slide 1",
    },
    "reel_script": {
        "duration": "15-30 seconds",
        "style": "Hook in first 2 sec, relatable scenario, soft CTA at end",
    },
    "facebook_post": {
        "style": "Longer text ok, storytelling, community feel",
    },
    "whatsapp_broadcast": {
        "style": "Short, personal, like a message from a friend",
    },
    "twitter_thread": {
        "tweets": "4-7",
        "style": "Punchy, each tweet standalone but builds a narrative",
    },
    "meme": {
        "style": "Indian meme template, relatable scenario, subtle branding",
    },
    "youtube_short_script": {
        "duration": "30-60 seconds",
        "style": "Story format, dialogue-based, real scenario",
    },
}

# ── Content Calendar Slots ──────────────────────────────────────
POSTING_SCHEDULE = {
    "monday": [
        {"time": "09:00", "type": "motivation", "platform": "instagram"},
        {"time": "19:00", "type": "relatable_scenario", "platform": "facebook"},
    ],
    "tuesday": [
        {"time": "10:00", "type": "carousel", "platform": "instagram"},
        {"time": "18:00", "type": "meme", "platform": "instagram"},
    ],
    "wednesday": [
        {"time": "09:00", "type": "reel_script", "platform": "instagram"},
        {"time": "20:00", "type": "whatsapp_broadcast", "platform": "whatsapp"},
    ],
    "thursday": [
        {"time": "10:00", "type": "twitter_thread", "platform": "twitter"},
        {"time": "19:00", "type": "relatable_scenario", "platform": "facebook"},
    ],
    "friday": [
        {"time": "09:00", "type": "motivation", "platform": "instagram"},
        {"time": "18:00", "type": "reel_script", "platform": "youtube_shorts"},
    ],
    "saturday": [
        {"time": "11:00", "type": "carousel", "platform": "instagram"},
        {"time": "17:00", "type": "money_tip", "platform": "twitter"},
    ],
    "sunday": [
        {"time": "10:00", "type": "meme", "platform": "instagram"},
        {"time": "19:00", "type": "story", "platform": "facebook"},
    ],
}

# ── SEO Keywords ────────────────────────────────────────────────
SEO_KEYWORDS = {
    "high_intent": [
        "instant personal loan app India",
        "loan without CIBIL score",
        "emergency loan for salary delay",
        "small loan app for gig workers",
        "personal loan kaise le",
        "loan app without salary slip",
        "5000 ka loan kaise milega",
        "rent ke liye loan",
        "medical emergency loan India",
        "bike EMI ke liye loan",
    ],
    "informational": [
        "personal loan eligibility India",
        "how to build CIBIL score",
        "gig worker financial planning",
        "EMI calculator small loan",
        "safe loan apps India 2026",
    ],
    "long_tail": [
        "delivery boy emergency loan without documents",
        "auto driver personal loan no salary slip",
        "first time loan kaise le bina CIBIL ke",
        "festival season instant loan app",
        "medical emergency mein turant loan kaise milega",
    ],
}

# ── Community Targets ───────────────────────────────────────────
COMMUNITY_TARGETS = {
    "reddit": {
        "subreddits": [
            "IndiaInvestments",
            "india",
            "IndianStreetBets",
            "personalfinanceindia",
        ],
        "keywords": [
            "personal loan",
            "emergency money",
            "salary delay",
            "need cash urgently",
            "loan app",
            "CIBIL score",
            "gig worker money",
        ],
    },
    "quora": {
        "topics": [
            "Personal Finance in India",
            "Loans in India",
            "Financial Planning for Young Indians",
        ],
        "keywords": [
            "instant loan India",
            "personal loan without CIBIL",
            "small loan app safe",
        ],
    },
    "twitter": {
        "keywords": [
            "salary delay",
            "month end struggle",
            "EMI stress",
            "need money urgently",
            "payday loan India",
        ],
        "hashtags": [
            "#SalaryDelay",
            "#MonthEndStruggles",
            "#PersonalLoan",
            "#GigWorkerLife",
        ],
    },
    "facebook_groups": {
        "group_types": [
            "Gig worker groups",
            "City-specific finance groups",
            "Delivery partner communities",
            "Small business owner groups",
        ],
    },
}
