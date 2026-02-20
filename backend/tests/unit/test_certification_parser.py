from app.services.parser.certification_parser import CertificationParser


def test_extract_candidate_lines_from_full_text_picks_cert_lines_and_skips_skills():
    text = "\n".join(
        [
            "SKILLS: Python, AWS, SQL",
            "Certified Kubernetes Administrator (CKA)",
            "AWS Certified Solutions Architect - Associate (SAA-C03)",
            "Random sentence about aws usage in projects.",
            "Certification: Azure DevOps Engineer Expert (AZ-400)",
        ]
    )

    lines = CertificationParser.extract_candidate_lines_from_full_text(text)
    assert "Certified Kubernetes Administrator (CKA)" in lines
    assert "AWS Certified Solutions Architect - Associate (SAA-C03)" in lines
    assert "Certification: Azure DevOps Engineer Expert (AZ-400)" in lines
    assert all("SKILLS:" not in ln.upper() for ln in lines)
