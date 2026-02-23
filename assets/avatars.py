"""
3D Glassmorphic Avatars for LoanVerse AI - Bliss Mode
"""

# MAYA - The AI Agent (Glowing Cyan/Purple Node)
MAYA_AVATAR = """
<svg viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
    <defs>
        <radialGradient id="maya_glow" cx="50%" cy="50%" r="50%" fx="50%" fy="50%">
            <stop offset="0%" stop-color="#00E5FF" stop-opacity="0.8"/>
            <stop offset="100%" stop-color="#A855F7" stop-opacity="0"/>
        </radialGradient>
        <filter id="glass_blur">
            <feGaussianBlur in="SourceGraphic" stdDeviation="2" />
        </filter>
        <linearGradient id="maya_body" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stop-color="#2563EB"/>
            <stop offset="100%" stop-color="#9333EA"/>
        </linearGradient>
    </defs>
    
    <!-- Outer Glow -->
    <circle cx="50" cy="50" r="45" fill="url(#maya_glow)" opacity="0.4" />
    
    <!-- Core Sphere -->
    <circle cx="50" cy="50" r="35" fill="url(#maya_body)" stroke="rgba(255,255,255,0.3)" stroke-width="2"/>
    
    <!-- Inner Graphics (Neural Network Node) -->
    <path d="M50 25 L50 75 M25 50 L75 50 M32 32 L68 68 M68 32 L32 68" stroke="rgba(255,255,255,0.6)" stroke-width="2" stroke-linecap="round"/>
    <circle cx="50" cy="50" r="12" fill="#00E5FF" opacity="0.8" filter="url(#glass_blur)"/>
    <circle cx="50" cy="50" r="6" fill="#FFFFFF"/>
</svg>
"""

# USER - The Client (Frosted Glass Profile)
USER_AVATAR = """
<svg viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
    <defs>
        <linearGradient id="user_glass" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stop-color="rgba(255,255,255,0.2)"/>
            <stop offset="100%" stop-color="rgba(255,255,255,0.05)"/>
        </linearGradient>
        <linearGradient id="user_border" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stop-color="#00E5FF"/>
            <stop offset="100%" stop-color="#A855F7"/>
        </linearGradient>
    </defs>
    
    <!-- Background Circle -->
    <circle cx="50" cy="50" r="42" fill="url(#user_glass)" stroke="url(#user_border)" stroke-width="2"/>
    
    <!-- Head -->
    <circle cx="50" cy="40" r="16" fill="white" opacity="0.9"/>
    
    <!-- Body -->
    <path d="M26 80 C26 65, 36 58, 50 58 C64 58, 74 65, 74 80" fill="white" opacity="0.7"/>
</svg>
"""
