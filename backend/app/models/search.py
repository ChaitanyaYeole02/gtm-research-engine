from dataclasses import dataclass


@dataclass(frozen=True)
class QueryStrategy:
    """
    Represents a search strategy for a specific channel.
    """

    channel: str
    query_template: str

    def build_query(self, company_domain: str) -> str:
        company_name = company_domain.split(".")[0]
        
        return self.query_template.format(
            DOMAIN=company_domain, COMPANY_NAME=company_name
        )
