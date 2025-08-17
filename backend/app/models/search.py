from dataclasses import dataclass


@dataclass(frozen=True)
class QueryStrategy:
    """
    Represents a search strategy for a specific channel.
    """

    channel: str
    query_template: str
    relevance_score: float = 1.0

    def build_query(self, company_domain: str) -> str:
        # jobs_search doesn't use domain/company placeholders
        if self.channel == "jobs_search":
            return self.query_template
            
        # Other channels use domain/company substitution
        company_name = company_domain.split(".")[0]
        
        return self.query_template.format(
            DOMAIN=company_domain, COMPANY_NAME=company_name
        )
