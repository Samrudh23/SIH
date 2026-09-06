# PCR Compliance Rule Specification — SIH26034 MVP (v2)

This document serves as the formal **Legal Specification** for the compliance-checking engine of the **SIH26034 Software System**. This specification is designed to bridge the gap between statutory Indian Legal Metrology legislation and automated software rules (using computer vision, Optical Character Recognition, and Natural Language Processing).

---

# Legal-to-Software Design Principles

For the SIH26034 prototype to remain legally robust and prevent liability, the architecture must adhere strictly to these four foundational principles:

1. **Observations vs. Determinations:** The AI and OCR models do not make legal "determinations." Instead, they extract **structural observations** (text strings, layout contours, language script classifications, and bounding-box proportions). The legal rule engine then matches these observations against statutory thresholds to produce **preliminary compliance screening results**.
2. **Preservation of Evidence:** Every flagged potential violation must retain its associated visual and textual evidence (including pixel crops, bounding-box coordinates, extracted OCR text segments, raw contrast values, and model confidence scores). 
3. **De-escalation to Manual Review:** If a model's classification confidence falls below a set threshold, or if a rule involves physical properties not determinable from a 2D image (such as packaging flexibility or camera-perspective distortion), the system must de-escalate the asset to `NEEDS_MANUAL_REVIEW` instead of generating a false positive.
4. **Safety and Routing Prioritization:** Product category classification (identifying Medical Devices or Pan Masala) must happen first. This allows the system to execute "routing switches" that alter standard size exemptions or bypass standard PCR compliance checking entirely.

---

# Part 1: High-Priority MVP Compliance Rules

## REQ-MVP-01 — Mandatory Declaration Presence
### Legal Source
* **Rule/Sub-rule:** Rule 6(1)
* **Amendment/G.S.R.:** Principal Rules (G.S.R. 202(E))
* **Source Document:** `01_Packaged_Commodities_Rules_2011.pdf`, Page 42-44

### Legal Requirement
Every retail package must carry a definite, plain, and conspicuous declaration of the five core legal blocks.
> **EXACT QUOTED TEXT:**
> *"Every package shall bear thereon or on label securely affixed thereto, a definite, plain and conspicuous declaration made in accordance with the provisions of this chapter as, to- (a) the name and address of the manufacturer, or where the manufacturer is not the packer, the name and address of the manufacturer and packer and for any imported package the name and address of the importer shall be mentioned; (b) The common or generic names of the commodity contained in the package and in case of packages with more than one product, the name and number or quantity of each product shall be mentioned on the package; (c) The net quantity, in terms of the standard unit of weight or measure, of the commodity contained in the package or where the commodity is packed or sold by number, the number of the commodity contained in the package shall be mentioned; (d) The month and year in which the commodity is manufactured or pre-packed or imported shall be mentioned in the package: (e) the retail sale price of the package;"*

### Exceptions / Applicability
* **Exemptions:** Under Rule 26, the entire Packaged Commodities Rules do not apply to packages where the net weight or measure of the commodity is ten gram or ten millilitre or less, if sold by weight or measure.
> **EXACT QUOTED TEXT (Rule 26):**
> *"Nothing contained in these rules shall apply to any package containing a commodity if— (a) the net weight or measure of the commodity is ten gram or ten millilitre or less, if sold by weight or measure;"*
* **Sector Regulations:** Food, seeds, and cosmetics packages are subject to respective sector-specific regulations for specific sub-declarations (such as Prevention of Food Adulteration Act, 1954 / FSSAI, Seeds Act, 1966, and Drugs and Cosmetics Rules, 1945).
* **Pan Masala Exception:** Under G.S.R. 881(E) (Second Amendment, 2025), Pan Masala is explicitly excluded from the small package exemption under Rule 26(a).

### Software Interpretation
The system parses the label text to verify the presence of five mandatory logical fields: manufacturer/packer address, generic commodity name, net quantity, month/year of packing, and retail sale price (MRP).

### Automation Level
**ASSISTED**

### What the System Can Detect
* The presence of contiguous text blocks on the package surface.
* High confidence matches for addresses (using PIN code/city patterns), commodity names, dates, net weight units, and MRP structures.

### What the System Cannot Determine
* Whether a missing declaration is legally printed on a completely different side of the container not captured in the submitted image.

### Evidence
* Bounding boxes around each identified text block, extracted OCR text segments, and NLP block classification status.

### Possible System Results
* `COMPLIANT` (all 5 blocks detected on visible panels)
* `NEEDS_MANUAL_REVIEW` (one or more blocks missing from the submitted photograph; prompts inspector to scan other faces)

### Explanation Shown to Inspector
* **Compliant:** "All five mandatory declarations (Manufacturer Address, Generic Name, Net Quantity, Manufacture Date, and MRP) have been successfully identified on the package."
* **Needs Manual Review:** "The system could not identify one or more mandatory blocks on the visible packaging panels. Please manually inspect the container to ensure all required details are printed elsewhere."

### Legal Verification Note
CONFIRMED — Verbatim clauses match principal rules page 42-44.

---

## REQ-MVP-02 — Maximum Retail Price (MRP) Layout
### Legal Source
* **Rule/Sub-rule:** Rule 2(m) and Rule 6(1)(e)
* **Amendment/G.S.R.:** Principal Rules (G.S.R. 202(E))
* **Source Document:** `01_Packaged_Commodities_Rules_2011.pdf`, Page 40 and 43-44

### Legal Requirement
The retail sale price must use the rupee symbol (or statutory abbreviations) and must explicitly state that the price includes all taxes.
> **EXACT QUOTED TEXT:**
> *"(m) "retail sale price" means the maximum price at which the commodity in packaged form may be sold to the ultimate consumer and the price shall be printed on the package in the manner given below; 'Maximum or Max. retail price Rs. ...../₹ ......... inclusive of all taxes or in the form MRP Rs. ...../₹ ......... incl., of all taxes after taking into account the fraction of less than fifty paise to be rounded off to the preceding rupee and fraction of above 50 paise and up to 95 paise to the rounded off to fifty paise;"*

### Exceptions / Applicability
* **Exemptions:** Bidies and domestic liquefied petroleum gas cylinders bottled/marketed by public sector undertakings are exempt from declaring retail sale price (MRP).
* **Alcoholic Beverages:** Governed by State Excise Laws (the principal PCR rule applies only if State laws do not mandate price declarations).

### Software Interpretation
The system parses pricing text blocks to verify they match the exact legal layout templates and include the mandatory tax-inclusion modifier.

### Automation Level
**AUTOMATIC**

### What the System Can Detect
* Pricing strings matching the statutory patterns (e.g. `MRP Rs. 150.00 incl. of all taxes` or `₹ 150.00 inclusive of all taxes`).
* Absence of the words "inclusive of all taxes" or its legal abbreviations (`incl. of all taxes` / `incl., of all taxes`).

### What the System Cannot Determine
* Whether the printed value exceeds the actual statutory cap or administrative pricing parameters.

### Evidence
* Crop of the price block, bounding box coordinates, extracted OCR text, and regex match status.

### Possible System Results
* `COMPLIANT` (matches legal templates)
* `POTENTIAL_VIOLATION` (extracted price block lacks "inclusive of all taxes" or uses illegal layout variations)
* `NOT_APPLICABLE` (product class identified as Bidi or Domestic LPG)

### Explanation Shown to Inspector
* **Compliant:** "MRP declaration complies with Rule 2(m). It is formatted using the Rupee symbol and includes the mandatory tax declaration."
* **Potential Violation:** "The extracted price string lacks the mandatory tax-inclusion suffix. Rule 2(m) requires the exact phrase 'inclusive of all taxes' or its approved abbreviations."

### Legal Verification Note
CONFIRMED — Verbatim clause matches principal rule page 40.

---

## REQ-MVP-03 — Net Quantity Metric Unit Validation
### Legal Source
* **Rule/Sub-rule:** Rule 13(1), (4) & (5)
* **Amendment/G.S.R.:** Principal Rules (G.S.R. 202(E))
* **Source Document:** `01_Packaged_Commodities_Rules_2011.pdf`, Page 53-55

### Legal Requirement
Quantities must be declared using correct metric symbols. Traditional units of count (dozen, gross, etc.) are strictly prohibited.
> **EXACT QUOTED TEXT:**
> *"13. Statement of units of weight, measure or number.- (1) The units of weight or measure or number shall be specified in accordance with the units specified in sub-rule (2) or sub-rule (3), as the case may be."*
> *"(4) No number called the dozen, score, gross, great gross or the like shall be specified or indicated on any package."*
> *"(5) Symbol of units:- (i) No system of units other than the International System of Units shall be used in furnishing the net quantity of the package; (ii) For items sold by number the symbol should be N or U."*

### Exceptions / Applicability
* Applies to all packaged retail commodities.

### Software Interpretation
The system parses the unit suffix appended to quantity numerals to verify that it uses standard SI metric symbols and flags any traditional or prohibited unit terms.

### Automation Level
**AUTOMATIC**

### What the System Can Detect
* Non-compliant written unit symbols (e.g., `gms`, `KG`, `ML`, `g.m.s`, `Nos.`, `pcs`).
* Prohibited counting terms (`dozen`, `gross`, `score`) printed on the quantity line.
* Correct SI symbols (`g`, `kg`, `ml`, `l`, `L`, `N`, `U`).

### What the System Cannot Determine
* The physical accuracy of the weight or count inside the container.

### Evidence
* Net quantity text region crop, OCR characters, and metric-vocabulary lookup result.

### Possible System Results
* `COMPLIANT` (utilizes correct symbols: `g`, `kg`, `ml`, `l`, `L`, `N`, or `U`)
* `POTENTIAL_VIOLATION` (utilizes prohibited traditional terms or illegal symbols like `gms` or `Nos.`)

### Explanation Shown to Inspector
* **Compliant:** "The quantity unit symbol complies with Rule 13."
* **Potential Violation:** "Prohibited unit symbol detected on the label. Standard metric units must use official symbols (e.g., 'g' instead of 'gms', 'N' or 'U' instead of 'Nos.'). Use of words like 'dozen' or 'gross' is illegal under Rule 13(4)."

### Legal Verification Note
CONFIRMED — Verbatim clause matches principal rule page 53-55.

---

## REQ-MVP-04 — Net Quantity Unit-Switching Boundary
### Legal Source
* **Rule/Sub-rule:** Rule 13(2), (3) Proviso
* **Amendment/G.S.R.:** Principal Rules (G.S.R. 202(E))
* **Source Document:** `01_Packaged_Commodities_Rules_2011.pdf`, Page 53-54

### Legal Requirement
Declarations must switch unit scale (e.g., grams to kilograms, milliliters to liters) at the 1 kg / 1 L boundaries. However, an option exists to use the smaller scale if the weight is exactly equal to 1 kg or 1 L.
> **EXACT QUOTED TEXT:**
> *"(2) When expressing a quantity less than,- (a) one kilogram, the unit of weight shall be the gram; ... (f) one litre, the unit of volume shall be the millilitre."*
> *"(3) When expressing a quantity of equal to or more than- (a) one kilogram, the unit of weight shall be the kilogram and any fraction of a kilogram shall be expressed in terms of decimal of sub-multiples of kilogram or in terms of grams; ... (e) one litre, the unit of volume shall be the litre and any fraction of a litre shall be expressed in terms of decimal of sub-multiple of the litre: Provided that where the quantity to be expressed is equal to one kilogram, one metre, one square metre, one cubic decimetre, one cubic metre or one litre, as the case may be, such quantity may be expressed at the option of the manufacturer or the packer or the importer, as the case may be, in terms of gram, centimetre, square decimetre, cubic centimetre, cubic decimetre or millilitre as the case may be."*

### Exceptions / Applicability
* **Option Proviso:** Quantities of **exactly** 1 kg, 1 m, or 1 L may legally be declared as `1000 g`, `100 cm`, or `1000 ml` at the manufacturer's discretion.

### Software Interpretation
The system parses the quantity value and its unit to verify that the unit matches the scale boundaries (e.g., flagging decimal values like `0.5 kg` instead of `500 g`, or values like `1500 ml` instead of `1.5 L`), while permitting the exact `1000 g` / `1000 ml` exception.

### Automation Level
**AUTOMATIC**

### What the System Can Detect
* Decimal quantities represented under the wrong scale boundary (e.g., `0.5 kg` instead of `500 g`, or `1500 ml` instead of `1.5 L`).
* Legitimate use of the exact `1000 g` / `1000 ml` option.

### What the System Cannot Determine
* Physical density variations affecting volume-to-weight conversions.

### Evidence
* Parsed numerical value, extracted metric unit, and boundary evaluation step.

### Possible System Results
* `COMPLIANT` (aligned with boundary rules, or utilizes the exact 1 kg/1 L proviso)
* `POTENTIAL_VIOLATION` (decimal scaling violation, e.g. `0.25 kg` or `1250 ml`)

### Explanation Shown to Inspector
* **Compliant:** "Quantity expression scale matches boundary thresholds under Rule 13."
* **Potential Violation:** "Scaling transition violation detected. Rule 13(2) mandates that quantities below 1 kg must be declared in grams (e.g., '500 g' instead of '0.5 kg'), and those below 1 L must be declared in milliliters."

### Legal Verification Note
CONFIRMED — Verbatim clause matches principal rule page 53-54.

---

## REQ-MVP-05 — Prohibited Quantity Qualifiers
### Legal Source
* **Rule/Sub-rule:** Rule 12(6)
* **Amendment/G.S.R.:** Principal Rules (G.S.R. 202(E))
* **Source Document:** `01_Packaged_Commodities_Rules_2011.pdf`, Page 53

### Legal Requirement
Quantity declarations must not be modified or accompanied by qualitative words that weaken or exaggerate the weight.
> **EXACT QUOTED TEXT:**
> *"(6) The declaration of quantity shall not contain any word or expression which tends to create an exaggerated, misleading or inadequate impression as to the quantity of the commodity contained in the package, for example, words or expressions like-'minimum', 'not less than', 'average', 'about', 'approximately' or other words of similar nature."*

### Exceptions / Applicability
* Standard retail pre-packaged commodities.

### Software Interpretation
The system parses the characters surrounding the net quantity declaration block to verify that no qualitative modifiers are used to qualify the weight.

### Automation Level
**AUTOMATIC**

### What the System Can Detect
* Prohibited qualitative words (`minimum`, `min`, `not less than`, `average`, `about`, `approximately`, `approx`) located within the immediate bounding box of the quantity value.

### What the System Cannot Determine
* The occurrences of these words elsewhere on the packaging when used completely outside the quantity context (e.g., in promotional body text).

### Evidence
* Quantity text region crop, isolated surrounding text, and keyword match log.

### Possible System Results
* `COMPLIANT` (no qualitative modifiers detected on the quantity line)
* `POTENTIAL_VIOLATION` (prohibited word detected on the quantity line)

### Explanation Shown to Inspector
* **Compliant:** "The quantity declaration contains no illegal qualitative qualifiers."
* **Potential Violation:** "The quantity is qualified by a prohibited word. Rule 12(6) strictly forbids using terms like 'minimum', 'about', or 'approximately' to qualify the declared net quantity."

### Legal Verification Note
CONFIRMED — Verbatim clause matches principal rule page 53.

---

## REQ-MVP-06 — Date Declaration & Rubber-Stamp Proviso
### Legal Source
* **Rule/Sub-rule:** Rule 6(1)(d)
* **Amendment/G.S.R.:** Principal Rules (G.S.R. 202(E))
* **Source Document:** `01_Packaged_Commodities_Rules_2011.pdf`, Page 43-44

### Legal Requirement
Every retail package must declare the month and year of manufacture, packing, or import. Applying this with a rubber stamp is legally permissible if it is not overwritten.
> **EXACT QUOTED TEXT:**
> *"(d) The month and year in which the commodity is manufactured or pre-packed or imported shall be mentioned in the package: ... Provided also that a manufacturer may indicate the month and year using a rubber stamp without overwriting:"*

### Exceptions / Applicability
* **Exemptions:** Under Rule 6(1) Proviso (A), no declaration of date is required for bidies, incense sticks (agarbatti), and domestic LPG cylinders of 14.2kg or 5kg filled by public sector undertakings.

### Software Interpretation
The system locates the date block, parses the month/year format, and evaluates the characters for structural text overlapping to flag double-stamping or overwriting.

### Automation Level
**ASSISTED**

### What the System Can Detect
* Presence of month and year formats (e.g., `MM/YYYY`, `MM/YY`, `Month Year`).
* Overwritten characters (overlapping text contours) in the date block.

### What the System Cannot Determine
* The actual physical calendar day of packing.

### Evidence
* Date text block crop, extracted date string, date regex match status, and character stroke analysis.

### Possible System Results
* `COMPLIANT` (clear date structure, no overwriting)
* `POTENTIAL_VIOLATION` (date block missing, or has clear overlapping overwritten text)
* `NOT_APPLICABLE` (product class identified as Bidi, Incense, or Domestic LPG)

### Explanation Shown to Inspector
* **Compliant:** "Date of manufacture is clearly printed in a valid format."
* **Potential Violation:** "The date declaration displays severe stroke overlap or double stamping. Rule 6(1)(d) permits rubber stamping but strictly prohibits overwriting."

### Legal Verification Note
CONFIRMED — Verbatim clause matches principal rule page 43-44.

---

## REQ-MVP-07 — Consumer Care Contact Details
### Legal Source
* **Rule/Sub-rule:** Rule 6(2)
* **Amendment/G.S.R.:** Principal Rules (G.S.R. 202(E))
* **Source Document:** `01_Packaged_Commodities_Rules_2011.pdf`, Page 46

### Legal Requirement
Every retail package must prominently display a consumer grievance contact block containing specific postal and electronic channels.
> **EXACT QUOTED TEXT:**
> *"(2) Every package shall bear the name, address, telephone number, E-mail address, if available, of the person who can be or the office which can be, contacted, in case of consumer complaints."*

### Exceptions / Applicability
* Applies to all packaged retail commodities.

### Software Interpretation
The system parses the consumer contact block to verify that it explicitly contains distinct telephone and email structures alongside a physical contact address.

### Automation Level
**AUTOMATIC**

### What the System Can Detect
* The presence of consumer care keywords (`customer support`, `helpline`, `consumer care`, `contact us`).
* The physical presence of a telephone number pattern and email pattern.

### What the System Cannot Determine
* Whether the printed telephone number or email address is actively monitored or connected.

### Evidence
* Consumer care block crop, parsed phone and email substrings.

### Possible System Results
* `COMPLIANT` (possesses name/office, telephone, and email fields)
* `POTENTIAL_VIOLATION` (block detected but lacks telephone number or email fields)
* `NEEDS_MANUAL_REVIEW` (system cannot find a clear consumer care card structure)

### Explanation Shown to Inspector
* **Compliant:** "Consumer care contact details are complete under Rule 6(2)."
* **Potential Violation:** "Missing mandatory consumer care fields. The grievance contact block must contain a valid telephone number and email address."

### Legal Verification Note
CONFIRMED — Verbatim clause matches principal rule page 46.

---

## REQ-MVP-08 — Manufacturer Address Block Layout
### Legal Source
* **Rule/Sub-rule:** Rule 10(1) Explanation
* **Amendment/G.S.R.:** Principal Rules (G.S.R. 202(E))
* **Source Document:** `01_Packaged_Commodities_Rules_2011.pdf`, Page 50-51

### Legal Requirement
The address must represent the complete physical postal address of the factory premises.
> **EXACT QUOTED TEXT:**
> *"Explanation.- In this sub-rule, 'complete address' means, the postal address at which the factory is situated, and, in any other case, the name of the street, number (if any) assigned to the premises of the manufacturer or packer and either the name of the city and State where the business is carried on by the manufacturer or packer or the Postal Index Number [PIN] Code so that a consumer can identify and locate the manufacturer or packer or importer, as the case may be."*

### Exceptions / Applicability
* **Capacity Exemption:** Packages under 5 cubic cm are exempt from printing the full address, provided they carry an identification mark (Rule 10(1) Proviso 1).
* **Registered Short Address:** Shorter addresses sufficient to locate the party are permissible if officially registered under Rule 28.

### Software Interpretation
The system parses the address text block to verify the presence of street-level details, city, state, and a valid 6-digit Indian PIN Code.

### Automation Level
**AUTOMATIC**

### What the System Can Detect
* The presence of a 6-digit Indian PIN Code (matching `^[1-9][0-9]{5}$`).
* The existence of premises markers (street names, plot numbers, factory names).

### What the System Cannot Determine
* Whether the factory physically exists at that location or matches the company's registration records.

### Evidence
* Isolated address block crop, parsed PIN code, identified city and state tokens.

### Possible System Results
* `COMPLIANT` (address block contains street-level tokens and a valid PIN code)
* `POTENTIAL_VIOLATION` (address is too brief, lacking PIN or street indices)

### Explanation Shown to Inspector
* **Compliant:** "Address block contains complete postal details including street indices and PIN code."
* **Potential Violation:** "Address block is incomplete. Rule 10(1) mandates a complete physical address including street details, city, state, and PIN code."

### Legal Verification Note
CONFIRMED — Verbatim clause matches principal rule page 50-51.

---

## REQ-MVP-09 — Foreign Importer PDP Address Match
### Legal Source
* **Rule/Sub-rule:** Rule 10(1) Proviso 2
* **Amendment/G.S.R.:** Principal Rules (G.S.R. 202(E))
* **Source Document:** `01_Packaged_Commodities_Rules_2011.pdf`, Page 50

### Legal Requirement
If a product is imported but packaged or distributed in India, the local importer's name and complete address must reside on the Principal Display Panel.
> **EXACT QUOTED TEXT:**
> *"Provided further that where any commodity manufactured outside India is packed in India, the package shall also contain on the principal display panel the name and complete address of the packer or the importer in India."*

### Exceptions / Applicability
* Only applies to imported commodities packaged or distributed locally in India.

### Software Interpretation
If country of origin check reveals a non-Indian source (e.g. "Made in Germany"), the system parses the Principal Display Panel (PDP) to ensure the local importer's name and address are present on that specific panel.

### Automation Level
**AUTOMATIC**

### What the System Can Detect
* Country of origin text identifying a foreign country.
* The presence of an Indian corporate address block labeled with "Imported by" or "Packed in India by" on the same panel.

### What the System Cannot Determine
* Customs validation status or whether the importer is certified.

### Evidence
* Extracted country of origin string, local importer text block crop, and PDP panel association.

### Possible System Results
* `COMPLIANT` (imported product has its local Indian importer block on the PDP)
* `POTENTIAL_VIOLATION` (foreign origin detected, but no local importer/packer address block found on the PDP)
* `NOT_APPLICABLE` (product origin is explicitly declared as India)

### Explanation Shown to Inspector
* **Compliant:** "Imported product PDP contains complete details of the Indian importer/packer."
* **Potential Violation:** "Foreign country of origin detected, but the local Indian importer's address block is missing from the Principal Display Panel under Rule 10(1)."

### Legal Verification Note
CONFIRMED — Verbatim clause matches principal rule page 50.

---

## REQ-MVP-10 — Pan Masala Compliance Router
### Legal Source
* **Rule/Sub-rule:** Rule 26(a) Second Proviso
* **Amendment/G.S.R.:** G.S.R. 881(E) (Second Amendment, 2025)
* **Source Document:** `03_PCR_Second_Amendment_2025.pdf`, Page 2

### Legal Requirement
Standard weight/volume-based exemptions for small packages (equal to or under 10g or 10ml) do not apply to Pan Masala.
> **EXACT QUOTED TEXT:**
> *"Provided further that the provisions of this clause shall not apply to pan masala."*

### Exceptions / Applicability
* **Target Commodity:** Strictly applies to any package identified as Pan Masala.

### Software Interpretation
If the parsed commodity name is identified as "Pan Masala", the system bypasses standard weight-based label exemptions under Rule 26 and enforces 100% of the mandatory retail declarations.

### Automation Level
**AUTOMATIC** (Routing switch)

### What the System Can Detect
* The words "Pan Masala" or phonetic matches in the commodity name block.

### What the System Cannot Determine
* Legal disputes regarding the chemical definition of the scanned product.

### Evidence
* Commodity text block crop, classified category token, and routing flag state.

### Possible System Results
* `COMPLIANT` (Pan Masala package carries 100% of standard declarations)
* `POTENTIAL_VIOLATION` (small Pan Masala package under 10g/ml is missing mandatory declarations)

### Explanation Shown to Inspector
* **Compliant:** "Pan Masala product correctly bypasses small-package exemptions and carries all standard retail declarations."
* **Potential Violation:** "Pan Masala products are excluded from small-package exemptions by G.S.R. 881(E). Full retail declarations must be present regardless of package weight."

### Legal Verification Note
CONFIRMED — Verification with exact text matching G.S.R. 881(E).

---

## REQ-MVP-11 — Medical Devices Compliance Router
### Legal Source
* **Rule/Sub-rule:** Rule 2(h) Proviso, Rule 7(2) Proviso, and Rule 7(3) Proviso
* **Amendment/G.S.R.:** G.S.R. 778(E) (Amendment, 2025)
* **Source Document:** `02_PCR_Amendment_2025_24-10-2025.pdf`, Pages 2-3

### Legal Requirement
For packages containing medical devices, standard PCR 2011 declarations, PDP layouts, and font height/width rules are bypassed and routed strictly to the *Medical Devices Rules, 2017*.
> **EXACT QUOTED TEXT:**
> *"Provided that for packages containing medical devices, the provisions of the Medical Devices Rules, 2017, shall apply to make declarations;"* *(Inserted under Rule 2(h))*
> *"Provided that for packages containing medical devices, the provisions of the Medical Devices Rules, 2017, shall apply for the height of any numeral and letter to make declarations."* *(Inserted under Rule 7(2))*
> *"Provided that for packages containing medical devices, the provisions of the Medical Devices Rules, 2017, shall apply for the width of any numeral and letter to make declarations."* *(Inserted under Rule 7(3))*

### Exceptions / Applicability
* Applies strictly to packages classified as medical devices.

### Software Interpretation
If the parsed label identifies a medical device (such as via license formats like "Mfg. Lic. No. MD-X"), the system bypasses standard PCR layout verification and routes the package to a separate Medical Devices Rules evaluation.

### Automation Level
**AUTOMATIC** (Routing switch)

### What the System Can Detect
* Medical license formats (e.g., `Mfg. Lic. No.`, `MD-X` markers) or CDSCO identifiers.

### What the System Cannot Determine
* Complex clinical classifications under the Medical Devices Rules, 2017.

### Evidence
* Classification category token, identified medical license registration strings, and routing path flag.

### Possible System Results
* `NOT_APPLICABLE` (routed out of PCR 2011 checks to Medical Devices module)

### Explanation Shown to Inspector
* **Bypass Triggered:** "Medical Device detected on label. Bypassing standard Legal Metrology (Packaged Commodities) Rules, 2011 checking. Routed strictly to Medical Devices Rules, 2017."

### Legal Verification Note
CONFIRMED — Verification matching provisos inserted by G.S.R. 778(E).

---

## REQ-MVP-12 — Non-Standard Pack Size Disclaimer
### Legal Source
* **Rule/Sub-rule:** Rule 5, Proviso
* **Amendment/G.S.R.:** Principal Rules (G.S.R. 202(E))
* **Source Document:** `01_Packaged_Commodities_Rules_2011.pdf`, Page 42

### Legal Requirement
If a commodity listed in the Second Schedule is packed in a size other than those standard sizes prescribed, it must carry a prominent statutory non-standard package size disclaimer.
> **EXACT QUOTED TEXT:**
> *"Provided that if a commodity specified in the Second Schedule is packed in a size other than that prescribed in that Schedule, a declaration that 'Not a standard pack size under the Legal Metrology (packaged Commodities) Rules, 2011' or 'non standard size under the Legal Metrology (packaged Commodities) Rules, 2011' shall be made prominently on the label of such package."*

### Exceptions / Applicability
* Strictly applies to retail packages of commodities listed in the Second Schedule (such as Biscuits, Bread, Baby Food, Edible Oils, Tea, Coffee, Salt, Soaps).

### Software Interpretation
If the product is classified as a Second Schedule commodity, and the net quantity does not match the standard sizes defined in the schedule, the system parses the label to verify that the exact statutory non-standard disclaimer is present on the packaging.

### Automation Level
**ASSISTED**

### What the System Can Detect
* The declared net quantity and the classified commodity type.
* The presence or absence of the exact statutory disclaimer text strings on the visible label surfaces.

### What the System Cannot Determine
* Whether the classified category is legally disputable or whether the product qualifies for a specific sector-specific exclusion not represented in the Second Schedule.

### Evidence
* Classified commodity token, parsed net quantity value, and OCR text of the disclaimer bounding box.

### Possible System Results
* `COMPLIANT` (standard size detected, OR non-standard size detected with the correct prominent disclaimer string)
* `POTENTIAL_VIOLATION` (non-standard size detected without the required statutory disclaimer string)
* `NEEDS_MANUAL_REVIEW` (unable to confidently classify the commodity type or map it to Second Schedule thresholds)
* `NOT_APPLICABLE` (commodity is not listed in the Second Schedule)

### Explanation Shown to Inspector
* **Compliant:** "The package is in a prescribed standard size under the Second Schedule, or is a non-standard size that correctly carries the mandatory statutory disclaimer."
* **Potential Violation:** "The package size is non-standard for [Commodity] under the Second Schedule, and the mandatory non-standard size disclaimer is missing from the label."

### Legal Verification Note
CONFIRMED — Verbatim clause matches principal rule page 42 (Rule 5 Proviso).

---

## REQ-MVP-13 — Prohibition of Individual Correction Stickers
### Legal Source
* **Rule/Sub-rule:** Rule 6(3)
* **Amendment/G.S.R.:** Principal Rules (G.S.R. 202(E))
* **Source Document:** `01_Packaged_Commodities_Rules_2011.pdf`, Page 46

### Legal Requirement
Individual stickers are strictly prohibited on packages for making or altering any mandatory declarations, with a sole exception permitting a sticker for a revised lower MRP.
> **EXACT QUOTED TEXT:**
> *"(3) It shall not be permissible to affix individual stickers on the package for altering or making declaration required under these rules: Provided that for reducing the Maximum Retail Price (MRP), a sticker with the revised lower MRP (inclusive of all taxes) may be affixed and the same shall not cover the MRP declaration made by the manufacturer or the packer, as the case may be, on the label of the package."*

### Exceptions / Applicability
* Applies to all mandatory labeling fields. The sole exception is a sticker for a **reduced lower MRP**, provided it does not cover or obscure the original printed MRP.

### Software Interpretation
The system parses the package surface for physical overlay borders or texture differences placed on top of mandatory declarations, and evaluates whether any detected MRP overlay displays a price lower than the original printed price.

### Automation Level
**ASSISTED**

### What the System Can Detect
* The presence of physical sticker boundaries or paper overlays placed over text blocks on the package surface.
* The text of both the printed and stickered price blocks.

### What the System Cannot Determine
* Tactile details of label adhesion, or whether a boundary is part of the original package graphic design rather than a physical sticker.

### Evidence
* Bounding box coordinates of suspected overlay boundaries, OCR text from the original and stickered regions, and contrast analysis.

### Possible System Results
* `POTENTIAL_VIOLATION` (overlay detected on a mandatory field like weight or date, or an MRP sticker that increases price or completely covers the original printed MRP)
* `NEEDS_MANUAL_REVIEW` (overlay boundary detected on or near declarations; requires manual inspector verification)
* `COMPLIANT` (no stickers detected, or a compliant downward MRP revision sticker is detected)

### Explanation Shown to Inspector
* **Compliant:** "No non-compliant stickers detected on the package."
* **Potential Violation:** "A physical sticker overlay has been detected on a mandatory declaration field. Rule 6(3) strictly prohibits individual stickers for making or altering declarations, except for downward MRP revisions."

### Legal Verification Note
CONFIRMED — Verbatim clause matches principal rule page 46.

---

# Part 2: Assistive Visual Aids (No Automatic Violation/Compliance Claims)

The following two rules must be strictly restricted to **soft-flag assistive visual aids**. Because of camera-perspective limitations and the qualitative nature of the law, the system's output for these rules must **never** include `COMPLIANT` or `POTENTIAL_VIOLATION`.

## REQ-MVP-14 — Quantity Clearance Space (Quiet Zone)
### Legal Source
* **Rule/Sub-rule:** Rule 8(1)
* **Amendment/G.S.R.:** Principal Rules (G.S.R. 202(E))
* **Source Document:** `01_Packaged_Commodities_Rules_2011.pdf`, Page 48

### Legal Requirement
The area immediately surrounding the net quantity declaration must be completely free of printed information or graphics.
> **EXACT QUOTED TEXT:**
> *"Provided that the area surrounding the quantity declaration shall be free from printed information. (a) above and below by a space equal to at least the height of the numeral in the declaration, and (b) to the left and right by a space at least twice the height of numeral in the declaration."*

### Exceptions / Applicability
* Standard retail net quantity declarations.

### Software Interpretation
The system draws an interactive visual bounding box overlay representing vertical padding of 1H (where H is the numeral height) and horizontal padding of 2H around the isolated net quantity characters.

### Automation Level
**ASSISTED** (Visual aid only)

### What the System Can Detect
* The physical height of the net quantity numeral in pixels.
* The presence of other text strokes or graphical boundaries intersecting the 1H x 2H mask.

### What the System Cannot Determine
* Real millimeter clearance dimensions on distorted or curved 3D objects using a 2D image.

### Evidence
* Visual graphic card overlay rendering the clearance box on the inspector's screen.

### Possible System Results
* `NEEDS_MANUAL_REVIEW` (intersections found; requires inspector's verification)
* `NOT_DETECTED` (quantity numeral block could not be isolated)

### Explanation Shown to Inspector
* **Visual Aid Active:** "A clearance box (1H vertical clearance, 2H horizontal clearance) has been drawn around the net quantity. Please physically verify that this area is completely free of other printed logos, graphics, or text."

### Legal Verification Note
CONFIRMED — Verbatim clause matches principal rule page 48.

---

## REQ-MVP-15 — Readability & Text Contrast
### Legal Source
* **Rule/Sub-rule:** Rule 9(1)
* **Amendment/G.S.R.:** Principal Rules (G.S.R. 202(E))
* **Source Document:** `01_Packaged_Commodities_Rules_2011.pdf`, Page 49

### Legal Requirement
Mandatory declarations must be clearly prominent and legible, and price/quantity characters must conspicuously contrast with the background.
> **EXACT QUOTED TEXT:**
> *"9. Manner in which declaration shall be made.- (1) Every declaration which is required to be made on a package under these rules shall be -- (a) legible and prominent; (b) numerals of the retail sale price and net quantity declaration shall be printed, painted or inscribed on the package in a colour that contrasts conspicuously with the background of the label;"*

### Exceptions / Applicability
* **Proviso (a):** Information blown, formed, or molded directly on a glass or plastic surface is exempt from contrasting-color requirements.
> **EXACT QUOTED TEXT:**
> *"Provided that,-- (a) where any label information is blown, formed or moulded on a glass or plastic surface such information need not be required to be presented in a contrasting colour;"*

### Software Interpretation
The system runs relative character contrast profiling to highlight blurred or low-contrast text blocks to the inspector.

### Automation Level
**ASSISTED** (Visual aid only)

### What the System Can Detect
* Extreme low-contrast text blocks (e.g. white characters on a light gray background).
* Blurred or smudged print blocks.

### What the System Cannot Determine
* Conclusive compliance, as the law specifies no numerical luminance contrast ratio (such as WCAG standards). It is a purely qualitative standard.

### Evidence
* Local contrast analysis scores and character sharpness metrics.

### Possible System Results
* `NEEDS_MANUAL_REVIEW` (low contrast or blur detected; highlights region for verification)
* `NOT_DETECTED` (text blocks too obscure to perform contrast checks)

### Explanation Shown to Inspector
* **Visual Aid Active:** "The system detected a potential legibility or low-contrast warning in the highlighted region. Please manually confirm that all declarations are easily readable under normal retail lighting."

### Legal Verification Note
CONFIRMED — Verbatim clause and proviso match principal rule page 49.

---

# Explicitly Excluded from Phase 1

To maintain legal accuracy, prevent false violations, and preserve computational resource budget, the following checks are **explicitly excluded** from the Phase 1 MVP system:

1. **E-Commerce Sortable Origin Filter (Rule 6(10A)):** 
   * *Exclusion Reason:* Under G.S.R. 312(E) (Second Amendment, 2026), the searchable and sortable country of origin filter on e-commerce listings is officially postponed and **not legally active until 1st July, 2027**. Checking or flagging listings before this date represents a legal error.
2. **Director's Name on Retail Labels (Rule 27):**
   * *Exclusion Reason:* The Third Amendment of 2026 (G.S.R. 418(E)) requires registering the name of the Director responsible for violations. However, this is strictly a backend, portal-based **registration requirement under Rule 27**. There is no statutory requirement mandating that the Director's personal name be printed on the consumer retail package label itself.
3. **Legally Conclusive Font Size Measurement (Rule 7):**
   * *Exclusion Reason:* Millimeter measurements of characters cannot be verified with legal certainty from ordinary 2D smartphone photographs due to perspective warp, container curvature, camera lens distortions, and varying camera distances. The MVP will restrict height verification to interactive user calibration guides.
4. **Legally Conclusive Physical Net Quantity Verification (Rule 19):**
   * *Exclusion Reason:* Confirming the actual net quantity of the package contents is a physical testing procedure. Under Rule 19 and the Sixth Schedule, this requires physical scales, calibrated tares, climate controls, and legal averages across sample lots. It is physically impossible to verify net quantity from a photograph.
5. **Physical Sticker Edge Adhesion and Material Checks:**
   * *Exclusion Reason:* While the system can flag suspicious physical overlays using logical layout rules as an ASSISTED check, confirming whether a label is a permanent print, a compliant sticker, or a non-compliant sticker requires tactile, physical inspection.
6. **Molded Glass/Plastic Text Height Verification:**
   * *Exclusion Reason:* Embossed or molded characters (which require a 2 mm minimum height under Rule 7(3)) cannot be measured accurately without 3D depth sensors or optical profilometers.

---

# Legal-to-Software Design Summary

```
                      [ PACKAGING IMAGE CAPTURE ]
                                   |
                                   v
                      [ OCR & CATEGORY CLASSIFIER ]
                                   |
         +-------------------------+-------------------------+
         |                                                   |
         v                                                   v
 [ MEDICAL DEVICE ]                                   [ PAN MASALA ]
         |                                                   |
 (G.S.R. 778(E) Rule 2(h))                       (G.S.R. 881(E) Rule 26)
         |                                                   |
         v                                                   v
  Bypass standard PCR;                          Disable standard under-10g
  Route to Medical Devices                      small package exemptions;
  Rules, 2017 Module.                           Enforce 100% of standard PCR.
         |                                                   |
         +-------------------------+-------------------------+
                                   |
                                   v
                     [ OCR TEXT & BOUNDING BOXES ]
                                   |
         +-------------------------+-------------------------+
         |                                                   |
         v                                                   v
 [ REGEX & RULE ENGINE ]                            [ VISUAL OVERLAYS ]
         |                                                   |
  - REQ-02: MRP format check                          - REQ-14: Clearance Area
  - REQ-03: SI Unit syntax                            - REQ-15: Contrast Aid
  - REQ-04: Transition scaling                        (Results: NEEDS_REVIEW
  - REQ-05: Qualifying words                          or NOT_DETECTED only)
  - REQ-06: Date stamp override                       
  - REQ-07: Consumer Care fields
  - REQ-08: Address PIN code
  - REQ-09: Importer PDP check
  - REQ-12: Non-standard size check
  - REQ-13: Sticker detection check
         |                                                   |
         +-------------------------+-------------------------+
                                   |
                                   v
                     [ INSPECTOR SCREENING REPORT ]
            (COMPLIANT / POTENTIAL_VIOLATION / NEEDS_REVIEW)
```

This legal specification establishes a bulletproof framework for developers, ensuring that every code rule maps directly to Indian statutory law, preserves photographic evidence, and provides an assistive rather than a dictatorial tool for Legal Metrology Inspectors.
