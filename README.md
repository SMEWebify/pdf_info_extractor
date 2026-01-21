# PDF Data Extractor

An automated system for extracting informations from PDF invoices.

## Installation

### Prerequisites

- **Python 3.9+** 
- **Java Runtime Environment** (required for PDF table extraction)

### Step 1: Install Java

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install default-jre
```

**macOS:**
```bash
brew install java
```

**Windows:**
Download from [java.com](https://www.java.com/download/)

Verify installation:
```bash
java -version
```
If downloading java for the first time, you must add it to the PATH variable and restart computer. 

### Step 2: Clone/Download Project

```bash
git clone <your-repo-url>
cd invoice_extractor
```

### Step 3: Create Virtual Environment (Recommended)

using conda: 
```bash
conda env create -f environment.yml -y
conda activate pdf_extractor
```  

### Step 4: Set Up Environment Variables
Create a .env file in the project root:
```bash
touch .env
```
Add your API key (get one from [OpenRouter](https://openrouter.ai/)):
```env
OPENROUTER_API_KEY=sk-or-v1-your-actual-key-here
```

## Quick Start

1. Place PDF invoices in the invoices_files/
2. Run the extractor:
```bash
python main.py
```
3. Find result in output/invoices_info.csv