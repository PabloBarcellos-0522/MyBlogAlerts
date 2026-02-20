import os
from typing import Dict, List, Optional
from bs4 import BeautifulSoup
from .Scraping_Login import ScrapingLogin
from dotenv import load_dotenv

load_dotenv()


class CrawlerGrades:
    def __init__(self, login_handler: ScrapingLogin):
        self.login_handler = login_handler
        self.BASE_URL = os.getenv("BLOG_URL")
        if not self.BASE_URL:
            raise ValueError("BLOG_URL environment variable is not set.")

    def fetch_grades(self, username, password) -> Dict[str, Dict[str, str]]:
        """
        Fetches and parses the grades for a student after logging in.
        It dynamically finds the grades page URL from the student's dashboard.
        """
        session, dashboard_html = self.login_handler.login(username, password)
        if not session or not dashboard_html:
            raise Exception("Login failed: could not retrieve session or dashboard HTML.")

        print(f"Successfully logged in as {username}. Searching for grades page link.")

        # Dynamically find the grades page link from the dashboard
        grades_link_tag = dashboard_html.find("a", title="Boletins")
        if not grades_link_tag or not grades_link_tag.get('href'):
            raise Exception("Could not find the link to the grades page ('Boletins') on the dashboard.")
        
        grades_relative_path = grades_link_tag['href']
        grades_url = f"{self.BASE_URL}{grades_relative_path}"
        print(f"Grades page found: {grades_url}")

        try:
            response = session.get(grades_url, timeout=30)
            response.raise_for_status()
        except Exception as e:
            raise Exception(f"Failed to fetch grades page from {grades_url}: {e}")

        soup = BeautifulSoup(response.content, 'html.parser')
        all_grades: Dict[str, Dict[str, str]] = {}

        # Find all grade tables
        grade_tables = soup.find_all("table", class_="table table-hover table-bordered school-report")

        for table in grade_tables:
            # Find the header row to get column order (AV1, AV2, MP, Final)
            headers = [th.get_text(strip=True) for th in table.find("thead").find_all("th")]

            # Find the indices of the required columns
            av1_idx = -1
            av2_idx = -1
            mp_idx = -1
            pf_idx = -1
            final_idx = -1
            resultado_idx = -1
            discipline_idx = -1

            for i, header in enumerate(headers):
                if header == "AV1":
                    av1_idx = i
                elif header == "AV2":
                    av2_idx = i
                elif header == "MP":
                    mp_idx = i
                elif header == "PF":
                    pf_idx = i
                elif header == "Final":
                    final_idx = i
                elif header == "Resultado":
                    resultado_idx = i
                elif "Disciplina" in header:
                    discipline_idx = i  # "Disciplina" for portuguese

            if any(idx == -1 for idx in [av1_idx, av2_idx, mp_idx, final_idx, discipline_idx]):
                print(f"Warning: Could not find all required grade columns in a table. Headers found: {headers}")
                continue

            # Iterate through table rows
            for row in table.find("tbody").find_all("tr"):
                cols = row.find_all("td")

                if len(cols) > max(av1_idx, av2_idx, mp_idx, pf_idx, final_idx, resultado_idx, discipline_idx):
                    discipline_name = cols[discipline_idx].get_text(strip=True)

                    av1 = cols[av1_idx].get_text(strip=True) if av1_idx != -1 else ""
                    av2 = cols[av2_idx].get_text(strip=True) if av2_idx != -1 else ""
                    mp = cols[mp_idx].get_text(strip=True) if mp_idx != -1 else ""
                    pf = cols[pf_idx].get_text(strip=True) if pf_idx != -1 else ""
                    final = cols[final_idx].get_text(strip=True) if final_idx != -1 else ""
                    resultado = cols[resultado_idx].get_text(strip=True) if resultado_idx != -1 else ""

                    # Replace '-' with empty string or None as per requirement for null values
                    av1 = av1 if av1 != '-' else ""
                    av2 = av2 if av2 != '-' else ""
                    mp = mp if mp != '-' else ""
                    pf = pf if pf != '-' else ""
                    final = final if final != '-' else ""
                    resultado = resultado if resultado != '-' else ""

                    all_grades[discipline_name] = {
                        "AV1": av1,
                        "AV2": av2,
                        "MP": mp,
                        "PF": pf,
                        "FINAL": final,
                        "RESULTADO": resultado
                    }

        if not all_grades:
            print("No grades found after parsing all tables.")

        return all_grades
