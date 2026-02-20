import os
from typing import Dict, List, Optional
from bs4 import BeautifulSoup
from .Scraping_Login import ScrapingLogin
from dotenv import load_dotenv

load_dotenv()


class CrawlerAbsences:
    def __init__(self, login_handler: ScrapingLogin):
        self.login_handler = login_handler
        self.BASE_URL = os.getenv("BLOG_URL")
        if not self.BASE_URL:
            raise ValueError("BLOG_URL environment variable is not set.")

    def fetch_absences(self, username, password) -> Dict[str, Dict[str, str]]:
        """
        Fetches and parses the absences for a student after logging in.
        It dynamically finds the grades page URL from the student's dashboard.
        """
        session, dashboard_html = self.login_handler.login(username, password)
        if not session or not dashboard_html:
            raise Exception("Login failed: could not retrieve session or dashboard HTML.")

        print(f"Successfully logged in as {username}. Searching for absences page link.")

        # Dynamically find the grades page link from the dashboard
        grades_link_tag = dashboard_html.find("a", title="Boletins")
        if not grades_link_tag or not grades_link_tag.get('href'):
            raise Exception("Could not find the link to the absences page ('Boletins') on the dashboard.")

        grades_relative_path = grades_link_tag['href']
        grades_url = f"{self.BASE_URL}{grades_relative_path}"
        print(f"Absences page found: {grades_url}")

        try:
            response = session.get(grades_url, timeout=30)
            response.raise_for_status()
        except Exception as e:
            raise Exception(f"Failed to fetch absences page from {grades_url}: {e}")

        soup = BeautifulSoup(response.content, 'html.parser')
        all_absences: Dict[str, Dict[str, str]] = {}

        # Find all grade tables
        grade_tables = soup.find_all("table", class_="table table-hover table-bordered school-report")

        for table in grade_tables:
            # Find the header row to get column order
            headers = [th.get_text(strip=True) for th in table.find("thead").find_all("th")]

            # Find the indices of the required columns
            tf1_idx = -1
            tf2_idx = -1
            tf_idx = -1
            resultado_idx = -1
            discipline_idx = -1

            for i, header in enumerate(headers):
                if header == "TF1":
                    tf1_idx = i
                elif header == "TF2":
                    tf2_idx = i
                elif header == "TF":
                    tf_idx = i
                elif header == "Resultado":
                    resultado_idx = i
                elif "Disciplina" in header:
                    discipline_idx = i

            if any(idx == -1 for idx in [discipline_idx]):
                print(f"Warning: Could not find all required absence columns in a table. Headers found: {headers}")
                continue

            # Iterate through table rows
            for row in table.find("tbody").find_all("tr"):
                cols = row.find_all("td")

                if len(cols) > max(tf1_idx, tf2_idx, tf_idx, resultado_idx, discipline_idx):
                    discipline_name = cols[discipline_idx].get_text(strip=True)

                    tf1 = cols[tf1_idx].get_text(strip=True) if tf1_idx != -1 else ""
                    tf2 = cols[tf2_idx].get_text(strip=True) if tf2_idx != -1 else ""
                    tf = cols[tf_idx].get_text(strip=True) if tf_idx != -1 else ""
                    resultado = cols[resultado_idx].get_text(strip=True) if resultado_idx != -1 else ""

                    # Replace '-' with empty string or None as per requirement for null values
                    tf1 = tf1 if tf1 != '-' else ""
                    tf2 = tf2 if tf2 != '-' else ""
                    tf = tf if tf != '-' else ""
                    resultado = resultado if resultado != '-' else ""

                    all_absences[discipline_name] = {
                        "TF1": tf1,
                        "TF2": tf2,
                        "TF": tf,
                        "RESULTADO": resultado
                    }

        if not all_absences:
            print("No absences found after parsing all tables.")

        return all_absences
