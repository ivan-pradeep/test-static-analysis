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
        "Summarize the following static analysis findings for a code review comment.\n\n"
        "Your summary should include three sections:\n"
        "1. **Static Analysis Findings Summary:**\n"
        "   List all findings from tools like SpotBugs, including type/category, severity (if available), filename, line number, and the exact message.\n"
        "2. **Checkstyle Findings Summary:**\n"
        "   List all findings from Checkstyle, including type/category, severity (if available), filename, line number, and the exact message.\n"
        "3. **Most Important Issues:**\n"
        "   Group the issues by type/category, and for each group, specify:\n"
        "     - The number of occurrences\n"
        "     - A brief description of why this issue is important\n"
        "\nPresent the output in markdown format for easy reading in a pull request comment.\n"
        "\nHere are the findings:\n"
        "---\n"
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