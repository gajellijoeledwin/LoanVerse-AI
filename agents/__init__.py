"""
LoanVerse AI — Multi-Agent System
===================================
This package exposes all five specialist Worker Agents and the
Master Agent (Maya) in one clean import surface.

Usage:
    from agents import MasterAgent, SalesAgent, VerificationAgent, UnderwritingAgent, NegotiatorAgent

Author: LoanVerse Team
Purpose: Tata Capital Techathon 2026
"""

from agents.master import MasterAgent
from agents.sales import SalesAgent
from agents.verification import VerificationAgent
from agents.underwriting import UnderwritingAgent
from agents.negotiator import NegotiatorAgent

__all__ = [
    "MasterAgent",
    "SalesAgent",
    "VerificationAgent",
    "UnderwritingAgent",
    "NegotiatorAgent",
]

