from typing import (
    Any,
    Dict,
    List,
    Optional,
)


class SampleDataContext:

    def __init__(self):

        self.refs: Dict[
            str,
            Dict[str, Any],
        ] = {
            "users": {},
            "profiles": {},
            "skills": {},
            "user_skills": {},
            "skill_evidence": {},
            "skill_verifications": {},
            "resume_files": {},
            "opportunities": {},
            "opportunity_skills": {},
            "applications": {},
            "mentorships": {},
            "mentorship_sessions": {},
            "challenges": {},
            "challenge_skills": {},
            "challenge_submissions": {},
            "notifications": {},
        }

        self.uploaded_r2_keys: List[
            str
        ] = []

    def store(
        self,
        group: str,
        key: str,
        value,
    ) -> None:

        self.refs[
            group
        ][
            key
        ] = value

    def get(
        self,
        group: str,
        key: str,
    ):

        return self.refs[
            group
        ][
            key
        ]

    def get_optional(
        self,
        group: str,
        key: Optional[str],
    ):

        if not key:
            return None

        return (
            self.refs
            .get(
                group,
                {},
            )
            .get(
                key
            )
        )