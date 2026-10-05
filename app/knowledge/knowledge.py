import json
from pathlib import Path
from typing import Any


class KnowledgeBase:

    def __init__(self, path: str | Path):
        self.path = Path(path)

        with self.path.open(
            "r",
            encoding="utf-8",
        ) as file:
            self.data: dict[str, Any] = json.load(file)

    def get_context(
        self,
        topic: str | None = None,
        subtopic: str | None = None,
    ) -> str:
        """
        Return only the knowledge required for the requested topic.

        The goal is to keep LLM prompts small while preserving the
        underlying institutional knowledge in data.json.
        """

        if topic == "lab":
            data = {
                "lab": self.data.get("lab", {})
            }

        elif topic == "organization":
            organization = self.data.get(
                "organization",
                {},
            )

            if not isinstance(organization, dict):
                organization = {}

            if subtopic:
                data = {
                    "organization": self._organization_subset(
                        organization,
                        subtopic,
                    )
                }
            else:
                data = {
                    "organization": organization
                }

        elif topic == "farm":
            data = {
                "experimental_farm": self.data.get(
                    "experimental_farm",
                    {},
                )
            }

        elif topic == "faq":
            data = {
                "faq": self.data.get(
                    "faq",
                    [],
                )
            }

        elif topic is None:
            data = self.data

        else:
            data = {
                topic: self.data.get(
                    topic,
                    {},
                )
            }

        return json.dumps(
            data,
            indent=2,
            ensure_ascii=False,
        )

    @staticmethod
    def _organization_subset(
        organization: dict[str, Any],
        subtopic: str,
    ) -> dict[str, Any]:
        """
        Select a small, relevant portion of organization knowledge.
        """

        groups = {
            "identity": (
                "name",
                "parent_organisation",
                "broad_division",
                "location",
                "pin",
                "primary_research_subject",
                "description",
                "what_nrcy_does",
                "icar",
                "abbreviations",
            ),
            "director": (
                "current_director",
                "director_email",
                "current_director_source",
            ),
            "contact": (
                "name",
                "location",
                "pin",
                "director_email",
                "telephone_numbers",
                "contact_reconciliation",
            ),
            "research": (
                "primary_research_subject",
                "what_nrcy_does",
                "official_mandate",
                "major_research_areas",
                "research_publication_context",
            ),
            "people": (
                "important_people",
                "people_name_variants",
            ),
            "projects": (
                "relationships",
                "recent_achievements",
                "what_nrcy_does",
            ),
            "achievements": (
                "recent_achievements",
                "yak_churpi",
                "fibre_and_entrepreneurship",
            ),
            "farm": (
                "farm_and_facilities",
            ),
            "outreach": (
                "farmer_and_community_outreach",
                "geographic_scope",
            ),
        }

        keys = groups.get(subtopic)

        if keys is None:
            return organization

        return {
            key: organization[key]
            for key in keys
            if key in organization
        }

    def get_lab_field(self, field: str):
        lab = self.data.get(
            "lab",
            {},
        )
        return lab.get(field)

    def get_lab(self) -> dict:
        return self.data.get(
            "lab",
            {},
        )

    def find_faq(
        self,
        question: str,
    ) -> str | None:

        question = question.lower().strip()

        for item in self.data.get(
            "faq",
            [],
        ):
            faq_question = item[
                "question"
            ].lower()

            if question == faq_question:
                return item["answer"]

        return None