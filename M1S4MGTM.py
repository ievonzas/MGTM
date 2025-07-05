from bs4 import BeautifulSoup
import requests
import json
from deep_translator import GoogleTranslator
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import sys
import re
from tabulate import tabulate
from dotenv import load_dotenv
from colorama import Fore, Style

load_dotenv()
sender_email = os.getenv("SENDER_EMAIL")
sender_password = os.getenv("SENDER_PASSWORD")

def intro():
    print(Fore.RED + "!! IMPORTANT !!" + Style.RESET_ALL)
    print(Fore.YELLOW +"Dear user," + Style.RESET_ALL)
    print(Fore.YELLOW +"Please note that this program offers general medical advice and SHOULD NOT be treated as official medical guidance."+ Style.RESET_ALL)
    print(Fore.GREEN +"\n What's your ailment?:" + Style.RESET_ALL)
    print(Fore.GREEN +"1. Pain"+ Style.RESET_ALL)
    print(Fore.GREEN +"2. Fever"+ Style.RESET_ALL)
    print(Fore.GREEN +"3. Cold/ Flu"+ Style.RESET_ALL)
    print(Fore.GREEN +"4. Allergy"+ Style.RESET_ALL)  
    print(Fore.GREEN +"5. Menstrual Issues"+ Style.RESET_ALL)
    print(Fore.GREEN +"6. Wound Care and Skin Issues"+ Style.RESET_ALL)
    print(Fore.GREEN +"7. Digestion Issues"+ Style.RESET_ALL)
    print(Fore.GREEN +"8. Recommendations for 'Nice to have'"+ Style.RESET_ALL)
    print(Fore.BLUE +"Type 'Done' to exit"+ Style.RESET_ALL)

def ailment_choice(json_data): # could be a dictionary 1: pain, etc
    while True:
        ailment = input("Please choose from the list of ailments: ").strip().lower()

        if ailment == "1":
            print("Your ailment: Pain")
            return "pain"
        if ailment == "2":
            print("Your ailment: Fever")
            return "fever"
        if ailment == "3":
            print("Your ailment: Cold/ Flu")
            return "cold/flu"
        if ailment == "4":
            print("Your ailment: Allergy")
            return "allergy"
        if ailment == "5":
            print("Your ailment: Menstrual Issues")
            return "menstrual issues"
        if ailment == "6":
            print("Your ailment: Wound Care and Skin Issues")
            return "wounds"
        if ailment == "7":
            print("Your ailment: Digestion Issues")
            return "digestion issues"
        if ailment == "8":
            print("Your ailment: Recommendations for 'Nice to have'")
            return "recommendations"
        if ailment == "done":
            print("Thank you and goodbye!")
            return None
        else:
            print("Invalid choice. Please select a number from 1 to 8.")

def permission_for_emailing(): #could be also y/n or esc/enter
    print("The requested information will be sent via email.")
    print("Type in 'Yes' if you agree. Type in 'No' if you wish to see it in the terminal") 

    permission = input("Do you agree? (Type 'Yes' or 'No'): ").lower().strip()

    if permission == "yes":
        return "yes"
    elif permission == "no":
        return "no"
    else:
        print("Invalid input. Please type in 'Yes' or 'No'.")
        return permission_for_emailing()
            
def get_valid_email(json_data):
    while True:
        receiver_email = input("Enter your email address (or type 'Done' to go back): ").strip()
        
        if receiver_email.lower() == "done":
            print("Thank you and goodbye!")
            sys.exit()
        if validate_email(receiver_email):
            return receiver_email
        print("Invalid email address. Please try again.")
            
def show_in_terminal(meds):
    formatted_info = format_medication_info(meds)
    print(formatted_info)
    return None

def validate_email(user_email): # try/ except
    regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*\.[a-zA-Z]{2,}$'
    return re.match(regex, user_email)

def email_visuals(meds):
    email_body = format_medication_info(meds)

    intro_text = "!! REMINDER !! This IS NOT official medical advice. If you are experiencing serious health issues, seek medical help immediately!" 
    outro_text = "Get well soon!"
    
    ascii_art = r"""
    [IIIII]
     )""|(
    /     \
   /       \
   |`-...-'|
   |asprin |
 _ |`-...-'j    _
(\)`-.___.(I) _(/)
  (I)  (/)(I)(\)
     (I)      
    """

    full_body = intro_text + "\n\n" + email_body + "\n\n" + outro_text + "\n" + ascii_art
    return full_body

def send_mail(subject, meds, receiver):
    if not sender_email or not sender_password:
        raise ValueError("Sender email and password must be provided.")
    
    full_body = email_visuals(meds)

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)

        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver
        msg['Subject'] = subject
        msg.attach(MIMEText(full_body, 'plain'))

        server.sendmail(sender_email, receiver, msg.as_string())
        server.quit()
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")

def scrape_medication_info(urls):
    results = []
    for url in urls:
        try:
            url = url.strip().replace(" ", "")
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            name = soup.find('h1').text.strip() if soup.find('h1') else "N/A"

            detail_elements = soup.find_all(class_='detail__value')
            detail_texts = [el.get_text(strip=True) for el in detail_elements]

            vartojimas = detail_texts[0] if len(detail_texts) > 0 else "N/A"
            forma = detail_texts[1] if len(detail_texts) > 1 else "N/A"
            stiprumas = detail_texts[2] if len(detail_texts) > 2 else "N/A"
            veiklioji_medžiaga = detail_texts[3] if len(detail_texts) > 3 else "N/A"

            results.append({
                "name": name,
                "milligrams": stiprumas,
                "form": forma,
                "active_ingredient": veiklioji_medžiaga,
                "intake": vartojimas,
                "url": url,
                "extra_details": detail_texts
            })

        except requests.exceptions.RequestException as e:
            print(f"Failed to scrape {url}: {e}")
    return results

def load_medication_data(file_path):
    return load_list_from_json(file_path)

def format_medication_info(meds):
    headers = ["Name", "Milligrams", "Form", "Active Ingredient", "Intake"]
    table = [
        [
            translate_text(med["name"]),
            translate_text(med["milligrams"]),
            translate_text(med["form"]),
            translate_text(med["active_ingredient"]),
            translate_text(med["intake"])
        ] 
        for med in meds
    ]

    formatted_table = tabulate(table, headers, tablefmt="grid") # to look good in the email, better to embed html

    url_lines = []
    for med in meds:
        url_lines.append("- " + med['url'])

    urls = "\n".join(url_lines)
    result = formatted_table + "\n\nRelevant URLs:\n" + urls
    return result

def handle_output(scraped_data):
    decision = permission_for_emailing()
    
    if decision == "yes":
        receiver_email = get_valid_email(None)
        send_mail("Medication Recommendations from MGTM", scraped_data, receiver_email)
    elif decision == "no":
        show_in_terminal(scraped_data)

def translate_text(text):
    try:
        return GoogleTranslator(source='lt', target='en').translate(text)
    except Exception as e:
        print(f"Could not translate: {e}")
        return text

def load_list_from_json(file_path):
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except Exception as e:
        print(f"Could not load JSON file: {e}")
        return {}

def main():
    json_data = load_medication_data("ailments.json")
    if not json_data:
        return

    intro()
    ailment = ailment_choice(json_data)
    if not ailment:
        return

    urls = json_data.get(ailment, [])
    scraped_data = scrape_medication_info(urls)
    if not scraped_data:
        print("No data found.")
        return

    handle_output(scraped_data)

if __name__ == "__main__":
    main()