from pydantic import BaseModel
from typing import List, Optional

class CompanySnapshot(BaseModel):
    name: Optional[str] = None
    headquarters: Optional[str] = None
    year_founded: Optional[str] = None
    notable_leadership: Optional[List[str]] = None

class WebsiteSummary(BaseModel):
    pages_scraped_reviewed: Optional[List[str]] = None
    key_observations: Optional[List[str]] = None

class Overview(BaseModel):
    company_snapshot: CompanySnapshot = CompanySnapshot()
    website_summary: WebsiteSummary = WebsiteSummary()

class CoreOfferings(BaseModel):
    primary_products_services: Optional[List[str]] = None
    key_features_capabilities: Optional[List[str]] = None
    target_use_cases: Optional[List[str]] = None

class AdditionalSolutions(BaseModel):
    secondary_products: Optional[List[str]] = None
    integrations: Optional[List[str]] = None

class ProductsAndServices(BaseModel):
    core_offerings: CoreOfferings = CoreOfferings()
    additional_solutions: AdditionalSolutions = AdditionalSolutions()

class TargetAudience(BaseModel):
    customer_segments: Optional[List[str]] = None
    customer_pain_points: Optional[List[str]] = None

class CompetitiveLandscape(BaseModel):
    direct_competitors: Optional[List[str]] = None
    differentiators: Optional[List[str]] = None

class MarketAndAudience(BaseModel):
    target_audience: TargetAudience = TargetAudience()
    competitive_landscape: Optional[CompetitiveLandscape] = None

class RevenueModel(BaseModel):
    model_type: Optional[str] = None
    pricing_tiers: Optional[List[str]] = None

class KeyPartnerships(BaseModel):
    partners_distributors: Optional[List[str]] = None
    promotional_offers: Optional[List[str]] = None

class BusinessModelAndPricing(BaseModel):
    revenue_model: RevenueModel = RevenueModel()
    key_partnerships: KeyPartnerships = KeyPartnerships()

class CompanyCulture(BaseModel):
    mission_values: Optional[List[str]] = None
    employee_spotlight: Optional[List[str]] = None

class GrowthRecruitment(BaseModel):
    career_opportunities: Optional[List[str]] = None
    industry_expertise: Optional[List[str]] = None

class TeamAndCulture(BaseModel):
    company_culture: CompanyCulture = CompanyCulture()
    growth_recruitment: GrowthRecruitment = GrowthRecruitment()

class HighLevelObservations(BaseModel):
    overall_positioning: Optional[str] = None
    potential_strengths: Optional[List[str]] = None
    potential_gaps_limitations: Optional[List[str]] = None

class HighLevelBusinessWebsiteScrapeReport(BaseModel):
    overview: Overview = Overview()
    products_and_services: ProductsAndServices = ProductsAndServices()
    market_and_audience: MarketAndAudience = MarketAndAudience()
    business_model_and_pricing: BusinessModelAndPricing = BusinessModelAndPricing()
    team_and_culture: TeamAndCulture = TeamAndCulture()
    high_level_observations_and_conclusion: HighLevelObservations = HighLevelObservations()
