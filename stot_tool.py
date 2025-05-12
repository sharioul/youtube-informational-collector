import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse
import whois
import socket
import json

# --- Streamlit Page Setup ---
st.set_page_config(page_title="STOT Info Gathering Tool", page_icon="🕵️", layout="wide")
st.title("🕵️‍♂️ STOT Information Gathering Tool")
st.markdown("Analyze Strategic, Technical, Operational, and Tactical info of a domain.")

# --- User Input ---
domain = st.text_input("Enter target domain (e.g., example.com):")

if domain:
    # Normalize domain
    if not domain.startswith("http"):
        url = "http://" + domain
    else:
        url = domain
    parsed_domain = urlparse(url).netloc

    # --- Functions ---

    def get_whois_data(domain):
        try:
            w = whois.whois(domain)
            return w
        except:
            return None

    def get_ip_info(domain):
        try:
            ip = socket.gethostbyname(domain)
            return ip
        except:
            return None

    def get_page_title(url):
        try:
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.text, "html.parser")
            return soup.title.string.strip() if soup.title else "No Title Found"
        except:
            return "Unavailable"

    def extract_emails(content):
        return list(set(re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-z]{2,}', content)))

    def extract_tech_stack(html):
        tech = []
        if "wp-content" in html:
            tech.append("WordPress")
        if "jquery" in html:
            tech.append("jQuery")
        if "cloudflare" in html:
            tech.append("Cloudflare")
        if "google-analytics" in html:
            tech.append("Google Analytics")
        return list(set(tech))

    def get_social_links(text):
        social = {}
        patterns = {
            "LinkedIn": r"linkedin\.com/[^/\s]+",
            "Twitter": r"twitter\.com/[^/\s]+",
            "Facebook": r"facebook\.com/[^/\s]+",
            "Instagram": r"instagram\.com/[^/\s]+",
        }
        for platform, pattern in patterns.items():
            matches = re.findall(pattern, text)
            if matches:
                social[platform] = list(set(matches))
        return social

    # --- Data Collection ---
    st.info("🔍 Gathering information... Please wait.")

    try:
        response = requests.get(url, timeout=10)
        html_content = response.text
    except:
        st.error("❌ Could not retrieve content from the provided domain.")
        html_content = ""

    whois_data = get_whois_data(parsed_domain)
    ip_address = get_ip_info(parsed_domain)
    page_title = get_page_title(url)
    emails = extract_emails(html_content)
    tech_stack = extract_tech_stack(html_content)
    social_links = get_social_links(html_content)

    # # --- Display Results ---
    # st.markdown("## 🧠 Strategic Info")
    # st.write(f"**Domain Title:** {page_title}")
    # if whois_data:
    #     st.json({
    #         "Registrar": whois_data.registrar,
    #         "Creation Date": str(whois_data.creation_date),
    #         "Expiry Date": str(whois_data.expiration_date),
    #         "Country": whois_data.country,
    #         "Name Servers": whois_data.name_servers
    #     })
    # else:
    #     st.warning("Whois data not available.")

    # st.markdown("## 🛠️ Technical Info")
    # st.write(f"**IP Address:** {ip_address}")
    # st.write(f"**Technology Stack:** {', '.join(tech_stack) if tech_stack else 'Unknown'}")

    st.markdown("## 🔁 Operational Info")
    st.write(f"**Emails found:** {', '.join(emails) if emails else 'None'}")
    st.write(f"**Social Profiles:**")
    st.json(social_links if social_links else {"message": "No social links found"})

    st.markdown("## 🎯 Tactical Info")
    st.write("Tactical info can include behavior monitoring, public CVEs, etc. Not included in this version.")

    # Download Option
    result_data = {
        "Domain": domain,
        "IP": ip_address,
        "Page Title": page_title,
        "Emails": emails,
        "Tech Stack": tech_stack,
        "Social Links": social_links,
    }

    st.download_button(
        label="📥 Download Report (JSON)",
        data=json.dumps(result_data, indent=4),
        file_name=f"{parsed_domain}_report.json",
        mime="application/json"
    )

# Footer
st.markdown("---")
st.caption("⚠️ This tool is for educational & cybersecurity awareness purposes only.")
