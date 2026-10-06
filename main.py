import flet as ft
import requests
from requests.auth import HTTPBasicAuth
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def main(page: ft.Page):
    page.title = "SAP Live Data"
    page.scroll = "adaptive"

    # SAP Credentials
    user_input = ft.TextField(label="SAP User ID", width=300)
    pass_input = ft.TextField(label="SAP Password", password=True, can_reveal_password=True, width=300)

    # Mandatory Parameters (Inke 'Technical Name' aapko SAP se confirm karke update karne honge)
    p_company = ft.TextField(label="Company Code", value="EEP1", width=300)
    p_fiscal_year = ft.TextField(label="Fiscal Year", value="2025", width=300)
    p_period_from = ft.TextField(label="Period From", value="1", width=300)
    p_period_to = ft.TextField(label="Period to", value="12", width=300)
    p_comp_year = ft.TextField(label="Comparative Year", value="2024", width=300)
    p_comp_from = ft.TextField(label="Comp. Period From", value="1", width=300)
    p_comp_to = ft.TextField(label="Comp. Period to", value="12", width=300)

    status_text = ft.Text(size=14)
    data_column = ft.Column(spacing=10)

    def fetch_data(e):
        if not user_input.value or not pass_input.value:
            status_text.value = "Kripya User ID aur Password dono daalein."
            status_text.color = ft.Colors.RED
            page.update()
            return

        status_text.value = "SAP se live data aa raha hai..."
        status_text.color = ft.Colors.BLUE
        data_column.controls.clear()
        page.update()

        # Yahan parameters ko unke 'Technical Names' ke sath URL me bheja ja raha hai.
        # Agar error aaye, toh '=' se pehle wale naam (jaise P_CompanyCode) ko SAP CDS View ke actual technical names se replace kar dena.
        params_str = (
            f"p_comp='{p_company.value}',"
            f"p_y1='{p_fiscal_year.value}',"
            f"p_per1='{p_period_from.value}',"
            f"p_per2='{p_period_to.value}',"
            f"p_y2='{p_comp_year.value}',"
            f"p_per1_n='{p_comp_from.value}',"
            f"p_per2_n='{p_comp_to.value}'"
        )
        url = f"https://eeperpapp01.eep.com.et:44308/sap/opu/odata/sap/ZSOCIE_1_V2_CDS/ZSOCIE_1_V2({params_str})/Results?$format=json"

        try:
            res = requests.get(
                url,
                auth=HTTPBasicAuth(user_input.value, pass_input.value),
                verify=False
            )

            if res.status_code == 200:
                json_data = res.json()
                records = json_data.get('d', {}).get('results', [])

                if records:
                    status_text.value = f"Total {len(records)} records mile!"
                    status_text.color = ft.Colors.GREEN
                    for item in records:
                        # __metadata column hatane ke liye
                        item.pop('__metadata', None)

                        # Har row ko card/box mein dikhana
                        card_content = "\n".join([f"{k}: {v}" for k, v in item.items()])
                        card = ft.Card(
                            content=ft.Container(
                                content=ft.Text(card_content, size=12),
                                padding=10
                            )
                        )
                        data_column.controls.append(card)
                else:
                    status_text.value = "Login success, par table mein koi data nahi mila."
                    status_text.color = ft.Colors.AMBER
            elif res.status_code == 401:
                status_text.value = "Error 401: User ID ya Password galat hai."
                status_text.color = ft.Colors.RED
            else:
                status_text.value = f"Error {res.status_code}: {res.text}"
                status_text.color = ft.Colors.RED

        except Exception as ex:
            status_text.value = f"Connection Failed: {ex}"
            status_text.color = ft.Colors.RED

        page.update()

    login_btn = ft.FilledButton("Login & Load Data", on_click=fetch_data)

    page.add(
        ft.Text("SAP OData Live Viewer", size=22, weight="bold"),
        ft.Row([user_input, pass_input]),
        ft.Text("Mandatory Parameters:", weight="bold"),
        ft.Row([p_company, p_fiscal_year]),
        ft.Row([p_period_from, p_period_to]),
        ft.Row([p_comp_year, p_comp_from, p_comp_to]),
        login_btn,
        status_text,
        data_column
    )

ft.run(main)
