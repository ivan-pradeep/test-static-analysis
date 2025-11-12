import xml.etree.ElementTree as ET
import openai
import os

def parse_spotbugs(xml_path):
    """
    Parses SpotBugs XML report, extracts bug type, message, and location.
    """
    findings = []
    tree = ET.parse(xml_path)
    root = tree.getroot()
    for bug in root.findall('BugInstance'):
        bug_type = bug.get('type')
        category = bug.get('category')
        message = bug.find('ShortMessage').text if bug.find('ShortMessage') is not None else ""
        class_name = bug.find('Class').get('classname') if bug.find('Class') is not None else ""
        line = bug.find('SourceLine').get('start') if bug.find('SourceLine') is not None else ""
        findings.append(f"[SpotBugs] {category}/{bug_type}: {message} in {class_name} at line {line}")
    return findings

def parse_checkstyle(xml_path):
    """
    Parses Checkstyle XML report, extracts all violations.
    """
    findings = []
    tree = ET.parse(xml_path)
    root = tree.getroot()
    # Each <file> contains violations as <error>
    for file in root.findall('file'):
        file_name = file.get('name')
        for error in file.findall('error'):
            line = error.get('line')
            severity = error.get('severity')
            message = error.get('message')
            source = error.get('source')
            findings.append(f"[Checkstyle] {severity}: {message} in {file_name} at line {line}")
    return findings

def summarize_findings(findings, openai_api_key):
    prompt = (

    prompt = (
        "You are helping generate a human-readable summary of static code analysis reports for a Java project.\n"
        "I will provide SpotBugs and Checkstyle report outputs (in XML, JSON, or plain text).\n\n"
        "Please:\n"
        "- Summarize the issues in a developer-friendly, GitHub-ready Markdown format, following this structure:\n"
        "### SpotBugs Report (vX.Y.Z)\n"
        "| File | Issue | Severity | Recommendation |\n"
        "|------|-------|----------|---------------|\n"
        "| <file> | <issue description> | <severity> | <fix suggestion> |\n"
        "... (group repeated issues per file if possible)\n"
        "### Checkstyle Report (vX.Y.Z)\n"
        "| File | Rule Violated | Severity | Fix Suggestion |\n"
        "|------|---------------|----------|---------------|\n"
        "| <file> | <rule violated> | <severity> | <how to fix> |\n"
        "... (group repeated issues per file if possible)\n"
        "### Developer Focus Areas\n"
        "- Summarize the top files or components with the most issues.\n"
        "- List 3–5 prioritized action points (e.g., fix null checks, add Javadocs, run formatter).\n"
        "### Reviewer Note\n"
        "- Add a short paragraph summarizing overall project quality.\n\n"
        "Instructions:\n"
        "- Ensure the output is clean Markdown (renders nicely on GitHub).\n"
        "- Do not include redundant details like timestamps or XML structure.\n"
        "- If any high-severity or critical issues exist, call them out clearly in your summary.\n"
        "- Group repeated issues per file if possible.\n"
        "\nHere are the findings:\n"
        "----\n"
        + "\n".join(findings) +
        "\n---"
    )
    client = openai.OpenAI(api_key=openai_api_key)
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=512,
        temperature=0.3,
    )
    summary = response.choices[0].message.content
    return summary

if __name__ == "__main__":
    # Paths to the XML reports
    #spotbugs_xml =  r"C:\Users\pradeep.b.krishnan\APAC_Hackathon\poc_demo_repo\test-static-analysis\build\reports\spotbugs\main.xml"
    #checkstyle_xml = r"C:\Users\pradeep.b.krishnan\APAC_Hackathon\poc_demo_repo\test-static-analysis\build\reports\checkstyle\main.xml"
    spotbugs_xml = "build/reports/spotbugs/main.xml"
    checkstyle_xml = "build/reports/checkstyle/main.xml"

    # Parse findings
    spotbugs_findings = parse_spotbugs(spotbugs_xml)
    checkstyle_findings = parse_checkstyle(checkstyle_xml)
    all_findings = spotbugs_findings + checkstyle_findings

    #print("\n--- SpotBugs Findings ---")
    #for f in spotbugs_findings:
        #print(f)

    #print("\n--- Checkstyle Findings ---")
    #for f in checkstyle_findings:
        #print(f)
    
    #print("\n--- Invoking LLM summarization ---")
    # OpenAI API key (from environment variable for security)
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise ValueError("OPENAI_API_KEY not set in environment variables.")

    # Summarize findings
    summary = summarize_findings(all_findings, openai_api_key)

    # Output the summary (for manual posting or further automation)
    print("\n===== Static Analysis Summary =====\n")
    print(summary)
    print("\n=================================================\n")