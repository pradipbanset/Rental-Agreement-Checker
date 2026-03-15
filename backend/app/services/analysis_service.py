"""
Analysis Service - Handles contract analysis storage
"""
import json
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.db_models import Analysis, RiskLevel, Document


class AnalysisService:
    @staticmethod
    def create_analysis(db: Session, document_id: str, analysis_result: dict) -> Analysis:
        """Create analysis record from LLM result"""
        clauses = analysis_result.get("clauses", [])
        
        # Calculate statistics
        high_risk = sum(1 for c in clauses if c.get("soft_risk") == "high")
        medium_risk = sum(1 for c in clauses if c.get("soft_risk") == "medium")
        illegal = sum(1 for c in clauses if c.get("illegal", False))
        
        # Determine risk level
        if high_risk > 0 or illegal > 0:
            risk_level = RiskLevel.HIGH
        elif medium_risk > 0:
            risk_level = RiskLevel.MEDIUM
        else:
            risk_level = RiskLevel.LOW
        
        # Extract rent and bond amounts
        rent_amount = None
        bond_amount = None
        
        for clause in clauses:
            if clause.get("type") == "rent_payment" and "amount" in clause.get("numeric_values", {}):
                amount = clause["numeric_values"]["amount"]
                if amount and amount >= 50:
                    rent_amount = amount
                    break
        
        for clause in clauses:
            if clause.get("type") == "bond" and "amount" in clause.get("numeric_values", {}):
                amount = clause["numeric_values"]["amount"]
                if amount and amount >= 50:
                    bond_amount = amount
                    break
        
        # Create analysis - JSONB handles serialization automatically
        analysis = Analysis(
            document_id=document_id,
            clauses=clauses,  # Just pass the list directly, JSONB handles it
            total_clauses=len(clauses),
            illegal_clauses=illegal,
            high_risk_clauses=high_risk,
            medium_risk_clauses=medium_risk,
            risk_level=risk_level,
            rent_amount=rent_amount,
            bond_amount=bond_amount
        )
        
        db.add(analysis)
        db.commit()
        db.refresh(analysis)
        
        return analysis
    
    @staticmethod
    def get_analysis(db: Session, document_id: str) -> Analysis:
        """Get analysis for a document"""
        analysis = db.query(Analysis).filter(Analysis.document_id == document_id).first()
        
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        # JSONB returns Python objects directly, no parsing needed
        return analysis


# Singleton instance
analysis_service = AnalysisService()