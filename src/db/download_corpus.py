import os
import requests

def download_financial_corpus():
    corpus_dir = "data/banking_corpus"
    os.makedirs(corpus_dir, exist_ok=True)
    
    pdf_sources = {
        "chase_deposit.pdf": "https://www.chase.com/content/dam/chase-ux/documents/personal/checking/deposit-account-agreement.pdf",
        "bofa_deposit.pdf": "https://business.bofa.com/content/dam/boamlimages/documents/PDFs/deposit_account_agreement.pdf",
        "wellsfargo_deposit.pdf": "https://www.wellsfargo.com/assets/pdf/small-business/agreement.pdf",
        "cfpb_credit_cards.pdf": "https://files.consumerfinance.gov/f/documents/cfpb_consumer-credit-card-market-report_2023.pdf",
        "occ_installment_loans.pdf": "https://www.occ.gov/publications-and-resources/publications/comptrollers-handbook/files/installment-lending/pub-ch-installment-lending.pdf",
        "fed_mortgages.pdf": "https://files.consumerfinance.gov/f/documents/cfpb_charm_booklet.pdf"
    }
    
    print(f"Starting download of {len(pdf_sources)} enterprise banking manuals...")
    for filename, url in pdf_sources.items():
        file_path = os.path.join(corpus_dir, filename)
        if os.path.exists(file_path):
            print(f"⏭️  Skipping {filename} (Already exists)")
            continue
            
        print(f"⬇️  Downloading {filename}...")
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers, stream=True)
            response.raise_for_status()
            
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"✅ Successfully saved {filename}")
        except Exception as e:
            print(f"❌ Failed to download {filename}: {e}")

if __name__ == "__main__":
    download_financial_corpus()