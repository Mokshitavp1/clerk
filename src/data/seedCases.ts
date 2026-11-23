import { LegalCaseRecord, QueryExecutionResponse } from '../types/legal';

export const SEED_LEGAL_CASES: LegalCaseRecord[] = [
  {
    case_name: 'ONGC_vs_Saw_Pipes_2003',
    display_title: 'Oil & Natural Gas Corporation Ltd. v. Saw Pipes Ltd.',
    citation: '(2003) 5 SCC 705',
    jurisdiction: 'Supreme Court of India',
    year: 2003,
    summary_mode: 'llm',
    summary:
      'Landmark ruling under Section 74 of the Indian Contract Act, 1872 and Section 34 of the Arbitration and Conciliation Act, 1996. Holds that when a contract contains a genuine pre-estimate of liquidated damages and proving actual dollar loss in a public utility infrastructure project is impracticable or impossible, the aggrieved party may recover the stipulated liquidated damages without proving actual pecuniary loss, provided breach is established.',
    page_count: 14,
    chunk_count: 4,
    indexed_at: '2026-10-11T08:00:00Z',
    pages: [
      {
        page_number: 1,
        text: `OIL AND NATURAL GAS CORPORATION LTD. v. SAW PIPES LTD. [(2003) 5 SCC 705]. Supreme Court of India — M.B. Shah & Arun Kumar, JJ. Civil Appeal No. 7419 of 2001. The respondent company agreed to supply casing pipes to the appellant ONGC for offshore oil exploration deployment. Clause 14 of the contract explicitly stipulated that time was of the essence of the contract and that in the event of delay in delivery, ONGC was entitled to recover liquidated damages at the rate of 1% of the contract price per week of delay, subject to a ceiling of 10% of the total unit price, as an agreed and genuine pre-estimate of damages rather than a penalty.`
      },
      {
        page_number: 7,
        text: `Under Section 73 and Section 74 of the Indian Contract Act, 1872, the court must read the contractual terms alongside the nature of the transaction. When parties expressly stipulate in clear and unambiguous terms that a specified sum represents a genuine pre-estimate of damages caused by breach, the burden lies upon the party committing the breach to establish that no loss was likely to occur from such delay. Where the contract involves complex offshore oil drilling rigs or public utility operations, computing the exact rupee loss caused by delayed delivery of a single component is often impracticable.`
      },
      {
        page_number: 14,
        text: `The principles governing liquidated damages under Section 74 of the Contract Act may be summarized as follows: (1) Terms of the contract are required to be taken into consideration before arriving at the conclusion whether the party claiming damages is entitled to the same. (2) If the terms are clear and unambiguous stipulating the liquidated damages in case of the breach of the contract unless it is held that such estimate of damages/compensation is unreasonable or is by way of penalty, party who has committed the breach is required to pay such compensation and that is what is provided in Section 73 of the Contract Act. (3) In every case of breach of contract, the person aggrieved by the breach is not required to prove actual loss or damage suffered by him before he can claim a decree, and the Court is competent to award reasonable compensation in case of breach even if no actual damage is proved to have been suffered in consequence of the breach where it is impossible to assess actual loss.`
      }
    ]
  },
  {
    case_name: 'Kailash_Nath_Associates_2015',
    display_title: 'Kailash Nath Associates v. Delhi Development Authority',
    citation: '(2015) 4 SCC 136',
    jurisdiction: 'Supreme Court of India',
    year: 2015,
    summary_mode: 'llm',
    summary:
      'Authoritative reconciliation of Section 74 of the Indian Contract Act regarding liquidated damages and forfeiture of earnest money. Clarifies that damage or loss is a sine qua non for claiming compensation under Section 74: where it is possible to prove actual damage or loss, such proof is mandatory, and proving actual loss is dispensed with only where assessment is difficult or impossible.',
    page_count: 12,
    chunk_count: 4,
    indexed_at: '2026-10-11T08:01:00Z',
    pages: [
      {
        page_number: 1,
        text: `KAILASH NATH ASSOCIATES v. DELHI DEVELOPMENT AUTHORITY AND ANOTHER [(2015) 4 SCC 136]. Supreme Court of India — R.F. Nariman & Ranjan Gogoi, JJ. The appellant participated in a public auction conducted by the Delhi Development Authority (DDA) for a commercial plot and deposited Rs. 78,00,000 as 25% earnest money. Following extensions of time and subsequent cancellation, DDA forfeited the entire earnest money deposit despite subsequently re-auctioning the exact same plot for Rs. 11.78 crores—more than triple the appellant's original bid price—thereby suffering zero pecuniary loss.`
      },
      {
        page_number: 4,
        text: `Analyzing the ratio of Fateh Chand v. Balkishan Das and Maula Bux v. Union of India alongside ONGC Ltd. v. Saw Pipes Ltd., this Court reiterates that Section 74 of the Contract Act cuts through the labyrinth of English common law distinctions between liquidated damages and penalties. Section 74 awards "reasonable compensation not exceeding the amount so named or, as the case may be, the penalty stipulated for." Consequently, all stipulations by way of penalty or liquidated damages are subject to the overarching statutory ceiling of reasonable compensation.`
      },
      {
        page_number: 7,
        text: `Statement of Law on Section 74 of the Indian Contract Act: (1) Where a sum is named in a contract as a liquidated amount payable by way of damages, the party complaining of a breach can receive as reasonable compensation such liquidated amount only if it is a genuine pre-estimate of damages fixed by both parties and found to be such by the Court. (2) Whether a sum is a penalty or a genuine pre-estimate, Section 74 only dispenses with proof of actual loss or damage where it is difficult or impossible to prove actual loss in the circumstances of the case. (3) Where it is possible to prove actual damage or loss, such proof is not dispensed with, and damage or loss remains a sine qua non for the applicability of Section 74. (4) Forfeiture of earnest money is permissible only if the amount is reasonable; automatic forfeiture of a substantial deposit where the public authority suffered zero loss and instead realized a windfall profit on re-auction is arbitrary and impermissible under Section 74.`
      }
    ]
  },
  {
    case_name: 'Fateh_Chand_vs_Balkishan_Das_1963',
    display_title: 'Fateh Chand v. Balkishan Das',
    citation: 'AIR 1963 SC 1405',
    jurisdiction: 'Supreme Court of India (Constitution Bench)',
    year: 1963,
    summary_mode: 'llm',
    summary:
      'Foundational five-judge Constitution Bench decision interpreting Section 74 of the Indian Contract Act, 1872. Holds that clauses authorizing forfeiture of monies paid in advance (beyond nominal earnest money paid at contract formation) operate in the nature of a penalty, requiring the claimant to prove legal injury so the Court may assess reasonable compensation.',
    page_count: 11,
    chunk_count: 3,
    indexed_at: '2026-10-11T08:02:00Z',
    pages: [
      {
        page_number: 1,
        text: `FATEH CHAND v. BALKISHAN DAS [AIR 1963 SC 1405 : (1964) 1 SCR 515]. Five-Judge Constitution Bench — P.B. Gajendragadkar, K.N. Wanchoo, K.C. Das Gupta, J.C. Shah & N. Rajagopala Ayyangar, JJ. Under an agreement of sale of leasehold land and buildings in Delhi for Rs. 1,12,500, the vendee paid Rs. 1,000 as earnest money upon execution and a further sum of Rs. 24,000 upon delivery of possession. The sale deed stipulated that if the vendee failed to register the deed by the fixed date, the entire sum of Rs. 25,000 would stand forfeited.`
      },
      {
        page_number: 5,
        text: `Section 74 of the Indian Contract Act undoubtedly says that the aggrieved party is entitled to receive compensation from the party who has broken the contract, whether or not actual damage or loss is proved to have been caused by the breach. It merely dispenses with proof of "actual loss or damage"; it does not justify the award of compensation when in consequence of the breach no legal injury at all has resulted, because compensation for breach of contract can be awarded to make good loss or damage which naturally arose in the usual course of things.`
      },
      {
        page_number: 9,
        text: `The words "to be paid in case of such breach, or if the contract contains any other stipulation by way of penalty" inserted by the 1899 Amendment bring every covenant for forfeiture of deposits or part-payments made subsequent to earnest money within the ambit of Section 74. While the vendor was entitled to forfeit the initial Rs. 1,000 paid strictly as earnest money guaranteeing contract formation, the forfeiture of the additional Rs. 24,000 paid toward the purchase price was a stipulation by way of penalty. In the absence of evidence showing loss of market value, the vendor cannot retain the Rs. 24,000 windfall.`
      }
    ]
  },
  {
    case_name: 'NetJets_vs_LHC_Delaware_Veil',
    display_title: 'NetJets Aviation, Inc. v. LHC Communications, LLC (Delaware Veil Piercing)',
    citation: '537 F.3d 168 (Del. / 2d Cir.) & Wallace v. Wood, 752 A.2d 1175 (Del. Ch.)',
    jurisdiction: 'Delaware Court of Chancery / Federal Appellate',
    year: 2008,
    summary_mode: 'llm',
    summary:
      'Establishes the two-pronged Delaware standard for piercing the corporate veil under the alter-ego doctrine: (1) whether the parent/owner and the entity operated as a single economic entity considering undercapitalization, insolvency, siphoning of funds, and corporate formalities; and (2) whether an overall element of injustice, fraud, or sham existence is present.',
    page_count: 9,
    chunk_count: 3,
    indexed_at: '2026-10-11T08:03:00Z',
    pages: [
      {
        page_number: 1,
        text: `DELAWARE CORPORATE VEIL PIERCING DOCTRINE — NETJETS AVIATION, INC. v. LHC COMMUNICATIONS, LLC [537 F.3d 168] & WALLACE EX REL. CENCOM CABLE v. WOOD [752 A.2d 1175 (Del. Ch. 1999)]. Under Delaware law, persuading a court to disregard the corporate or LLC form and pierce the corporate veil is a difficult task reserved for exceptional circumstances. Delaware courts apply a two-pronged alter-ego test requiring the plaintiff to demonstrate both (1) that the corporation and its shareholders operated as a "single economic entity," and (2) that the corporate form was used to sanction a fraud, promote injustice, or evade a legal obligation.`
      },
      {
        page_number: 3,
        text: `In evaluating the first prong—whether the entity operated as a single economic unit—Delaware courts examine five primary factors: (a) whether the corporation was adequately capitalized for the corporate undertaking (undercapitalization); (b) whether the corporation was solvent at the time of the questioned transactions; (c) whether dividends were paid, corporate records kept, officers and directors functioned properly, and other corporate formalities were observed; (d) whether the dominant shareholder siphoned corporate funds for personal expenses; and (e) whether the corporation simply functioned as a facade for the dominant shareholder.`
      },
      {
        page_number: 6,
        text: `Crucially, under Delaware precedent (Wallace v. Wood, 752 A.2d at 1184), mere undercapitalization or insolvency alone is insufficient to pierce the corporate veil. Even where an entity is severely undercapitalized at formation or lacks formal board minutes, the plaintiff must satisfy the second prong by proving an "overall element of injustice or unfairness." The fraud or injustice must consist of an abuse of the corporate form itself—such as intentionally forming an undercapitalized shell company to shield assets while siphoning revenues—rather than merely the underlying breach of contract or unpaid debt.`
      }
    ]
  },
  {
    case_name: 'NY_CPLR_214a_Medical_Malpractice',
    display_title: 'Borgia v. City of New York & NY CPLR § 214-a',
    citation: '12 N.Y.2d 151 & N.Y. C.P.L.R. § 214-a',
    jurisdiction: 'New York Court of Appeals',
    year: 2018,
    summary_mode: 'llm',
    summary:
      'Governs the statute of limitations for medical, dental, and podiatric malpractice in New York under CPLR § 214-a. Sets the standard 2 years and 6 months limitation period from the act or omission, codifies the Continuous Treatment Doctrine, the 1-year Foreign Object discovery rule, and Lavern’s Law cancer misdiagnosis discovery rule.',
    page_count: 8,
    chunk_count: 3,
    indexed_at: '2026-10-11T08:04:00Z',
    pages: [
      {
        page_number: 1,
        text: `NEW YORK MEDICAL MALPRACTICE LIMITATIONS — N.Y. CPLR § 214-a & BORGIA v. CITY OF NEW YORK [12 N.Y.2d 151]. Under New York Civil Practice Law and Rules (CPLR) § 214-a, an action for medical, dental, or podiatric malpractice must be commenced within two years and six months (30 months) of the act, omission, or failure complained of. Unlike general negligence claims in New York (which carry a three-year statute of limitations under CPLR § 214), medical malpractice claims accrue on the date the alleged malpractice occurs, subject to three strictly delineated statutory and judicial exceptions.`
      },
      {
        page_number: 5,
        text: `Exception 1 — The Continuous Treatment Doctrine (Borgia v. City of New York): Where there is continuous treatment for the same illness, injury, or condition which gave rise to the said act, omission, or failure, the two-year-and-six-month period does not begin to run until the date of the last treatment. Routine checkups or general continuing doctor-patient relationships do not toll the statute; the ongoing treatment must specifically target the original condition. Exception 2 — Foreign Object Rule: Where the action is based upon the discovery of a foreign object (such as a surgical sponge or clamp, explicitly excluding chemical compounds, fixation devices, or prosthetic aids) left in the patient's body, the action may be commenced within one year of the date of discovery or of discovery of facts which would reasonably lead to such discovery, whichever is earlier.`
      },
      {
        page_number: 8,
        text: `Exception 3 — Lavern's Law (Cancer Misdiagnosis Discovery Rule, CPLR § 214-a(b)): Enacted in 2018, where the medical malpractice action is based upon the alleged negligent failure to diagnose cancer or a malignant tumor, whether by act or omission, the action may be commenced within two years and six months of the later of either: (i) when the person knows or reasonably should have known of such alleged negligent act or omission and knows or reasonably should have known that such act or omission has caused injury, provided that such action shall be commenced no later than seven years from the act, omission, or failure, or (ii) the date of the last treatment where there is continuous treatment for such injury or condition.`
      }
    ]
  }
];

export const INITIAL_QUERY_HISTORY: QueryExecutionResponse[] = [
  {
    id: 'hist-ny-malpractice',
    query: 'Statute of limitations for medical malpractice in New York',
    requested_mode: 'FAST',
    executed_mode: 'FAST',
    ambiguity: {
      detected: false,
      competing_cases: [],
      score_delta: 0.48,
      threshold: 0.1,
      explanation: 'Single precedent clearly dominates (NY_CPLR_214a_Medical_Malpractice scored 0.89 vs runner-up 0.41; Δ = 0.48 > 0.10).'
    },
    status: 'VERIFIED',
    verified: true,
    answer: `### Answer

Under **New York CPLR § 214-a**, an action for medical, dental, or podiatric malpractice must be commenced within **two years and six months (30 months)** of the alleged act, omission, or failure, rather than the three-year period applicable to ordinary negligence claims (NY_CPLR_214a_Medical_Malpractice, Page 1).

New York law recognizes three principal tolling and discovery exceptions to the 30-month accrual rule:

1. **Continuous Treatment Doctrine (*Borgia v. City of New York*):** Where the patient receives continuous treatment for the exact same illness, injury, or condition that gave rise to the alleged malpractice, the 2-year-and-6-month limitation period is tolled until the **date of the last treatment**. Routine checkups do not qualify (NY_CPLR_214a_Medical_Malpractice, Page 5).
2. **Foreign Object Exception:** When a claim arises from a foreign object (such as a surgical sponge or clamp, expressly excluding fixation devices, chemical compounds, or prosthetics) left inside the patient's body, the action may be commenced within **one year** of discovery or of facts that would reasonably lead to discovery (NY_CPLR_214a_Medical_Malpractice, Page 5).
3. **Lavern's Law (Cancer & Malignant Tumor Misdiagnosis, CPLR § 214-a(b)):** For negligent failure to diagnose cancer or a malignant tumor, the 2-year-and-6-month period runs from when the patient knew or reasonably should have known of the negligent omission and resulting injury, subject to an absolute statutory outside cap of **seven years** from the act or omission (NY_CPLR_214a_Medical_Malpractice, Page 8).

Sources: NY_CPLR_214a_Medical_Malpractice, Page 1; NY_CPLR_214a_Medical_Malpractice, Page 5; NY_CPLR_214a_Medical_Malpractice, Page 8.`,
    citations: [
      {
        case_name: 'NY_CPLR_214a_Medical_Malpractice',
        page_number: 1,
        snippet: 'Under New York Civil Practice Law and Rules (CPLR) § 214-a, an action for medical, dental, or podiatric malpractice must be commenced within two years and six months (30 months) of the act, omission, or failure complained of.'
      },
      {
        case_name: 'NY_CPLR_214a_Medical_Malpractice',
        page_number: 5,
        snippet: 'Where there is continuous treatment for the same illness, injury, or condition which gave rise to the said act, omission, or failure, the two-year-and-six-month period does not begin to run until the date of the last treatment.'
      },
      {
        case_name: 'NY_CPLR_214a_Medical_Malpractice',
        page_number: 8,
        snippet: 'Enacted in 2018, where the medical malpractice action is based upon the alleged negligent failure to diagnose cancer or a malignant tumor... two years and six months of when the person knows or reasonably should have known... no later than seven years.'
      }
    ],
    stage1_shortlist: [
      {
        case_name: 'NY_CPLR_214a_Medical_Malpractice',
        display_title: 'Borgia v. City of New York & NY CPLR § 214-a',
        citation: '12 N.Y.2d 151 & N.Y. C.P.L.R. § 214-a',
        dense_score: 0.91,
        bm25_score: 0.86,
        hybrid_score: 0.89,
        summary: 'Governs the statute of limitations for medical, dental, and podiatric malpractice in New York under CPLR § 214-a.'
      },
      {
        case_name: 'NetJets_vs_LHC_Delaware_Veil',
        display_title: 'NetJets Aviation, Inc. v. LHC Communications, LLC (Delaware Veil Piercing)',
        citation: '537 F.3d 168 (Del. / 2d Cir.)',
        dense_score: 0.44,
        bm25_score: 0.35,
        hybrid_score: 0.41,
        summary: 'Establishes the two-pronged Delaware standard for piercing the corporate veil under the alter-ego doctrine.'
      }
    ],
    stage2_chunks: [
      {
        chunk_id: 'NY_CPLR_214a_Medical_Malpractice_p1_c0',
        case_name: 'NY_CPLR_214a_Medical_Malpractice',
        page_number: 1,
        chunk_index: 0,
        text: SEED_LEGAL_CASES[4].pages[0].text,
        word_count: 91,
        dense_score: 0.93,
        bm25_score: 0.88,
        final_score: 0.91,
        passed_floor: true,
        selected_for_prompt: true
      },
      {
        chunk_id: 'NY_CPLR_214a_Medical_Malpractice_p5_c0',
        case_name: 'NY_CPLR_214a_Medical_Malpractice',
        page_number: 5,
        chunk_index: 0,
        text: SEED_LEGAL_CASES[4].pages[1].text,
        word_count: 148,
        dense_score: 0.87,
        bm25_score: 0.82,
        final_score: 0.85,
        passed_floor: true,
        selected_for_prompt: true
      },
      {
        chunk_id: 'NY_CPLR_214a_Medical_Malpractice_p8_c0',
        case_name: 'NY_CPLR_214a_Medical_Malpractice',
        page_number: 8,
        chunk_index: 0,
        text: SEED_LEGAL_CASES[4].pages[2].text,
        word_count: 129,
        dense_score: 0.84,
        bm25_score: 0.79,
        final_score: 0.82,
        passed_floor: true,
        selected_for_prompt: true
      }
    ],
    dropped_below_floor_count: 0,
    verification_audit: {
      layer1_citation_match: {
        passed: true,
        has_sources_line: true,
        cited_pairs: [
          { case_name: 'NY_CPLR_214a_Medical_Malpractice', page_number: 1, exists_in_prompt_chunks: true, matching_chunk_id: 'NY_CPLR_214a_Medical_Malpractice_p1_c0' },
          { case_name: 'NY_CPLR_214a_Medical_Malpractice', page_number: 5, exists_in_prompt_chunks: true, matching_chunk_id: 'NY_CPLR_214a_Medical_Malpractice_p5_c0' },
          { case_name: 'NY_CPLR_214a_Medical_Malpractice', page_number: 8, exists_in_prompt_chunks: true, matching_chunk_id: 'NY_CPLR_214a_Medical_Malpractice_p8_c0' }
        ],
        details: 'All 3 cited (case_name, page_number) pairs deterministically matched prompt chunks.'
      },
      layer1b_body_length: {
        passed: true,
        word_count: 214,
        min_words: 15
      },
      layer2_llm_groundedness: {
        passed: true,
        supported_claims: [
          'CPLR § 214-a sets a 2-year-and-6-month (30-month) limitation period from the act or omission.',
          'Continuous treatment for the same condition tolls accrual until the last treatment under Borgia v. City of New York.',
          'Foreign object claims may be brought within 1 year of discovery, excluding fixation devices and prosthetics.',
          'Lavern’s Law allows 2.5 years from discovery of cancer misdiagnosis, capped at 7 years from the act or omission.'
        ],
        unsupported_claims: [],
        reasoning: 'Every statutory timeframe and exception is explicitly stated in Pages 1, 5, and 8 of NY_CPLR_214a_Medical_Malpractice.'
      },
      retry_count: 0,
      total_verification_ms: 420
    },
    reranker_enabled: false,
    latency_ms: 1180,
    timestamp: '2026-10-11T08:10:00Z'
  },
  {
    id: 'hist-sec74-damages',
    query: 'What is the test for liquidated damages under Section 74 of the Contract Act?',
    requested_mode: 'DEEP THINKING',
    executed_mode: 'DEEP THINKING',
    ambiguity: {
      detected: true,
      competing_cases: [
        {
          case_name: 'Kailash_Nath_Associates_2015',
          display_title: 'Kailash Nath Associates v. Delhi Development Authority',
          citation: '(2015) 4 SCC 136',
          dense_score: 0.92,
          bm25_score: 0.90,
          hybrid_score: 0.91,
          summary: 'Authoritative reconciliation of Section 74 of the Indian Contract Act regarding liquidated damages and forfeiture of earnest money.'
        },
        {
          case_name: 'ONGC_vs_Saw_Pipes_2003',
          display_title: 'Oil & Natural Gas Corporation Ltd. v. Saw Pipes Ltd.',
          citation: '(2003) 5 SCC 705',
          dense_score: 0.89,
          bm25_score: 0.87,
          hybrid_score: 0.88,
          summary: 'Landmark ruling under Section 74 of the Indian Contract Act, 1872 and Section 34 of the Arbitration and Conciliation Act.'
        },
        {
          case_name: 'Fateh_Chand_vs_Balkishan_Das_1963',
          display_title: 'Fateh Chand v. Balkishan Das',
          citation: 'AIR 1963 SC 1405',
          dense_score: 0.85,
          bm25_score: 0.83,
          hybrid_score: 0.84,
          summary: 'Foundational five-judge Constitution Bench decision interpreting Section 74 of the Indian Contract Act, 1872.'
        }
      ],
      score_delta: 0.03,
      threshold: 0.1,
      explanation: 'Competing precedents detected: Kailash_Nath_Associates_2015 (0.91) and ONGC_vs_Saw_Pipes_2003 (0.88) are separated by Δ = 0.03 ≤ 0.10 threshold.'
    },
    status: 'VERIFIED',
    verified: true,
    answer: `### Answer

Under **Section 74 of the Indian Contract Act, 1872**, the test for recovering liquidated damages requires evaluating whether the stipulated sum is a **genuine pre-estimate of damages** or a **penalty**, subject always to the statutory ceiling of **reasonable compensation** and proof of legal injury:

#### 1. Synthesis & Modern Controlling Standard (*Kailash Nath Associates v. DDA*, 2015)
- **Reasonable Compensation Ceiling:** A party complaining of breach may receive the stipulated liquidated sum only if it is a genuine pre-estimate of damages fixed by the parties and found to be such by the Court, never exceeding the named amount (Kailash_Nath_Associates_2015, Page 4; Kailash_Nath_Associates_2015, Page 7).
- **When Proof of Actual Loss is Required:** Damage or loss is a *sine qua non* for applicability of Section 74. Where it is **possible** to prove actual damage or loss, such proof is **not dispensed with** (Kailash_Nath_Associates_2015, Page 7). Where a public authority suffered zero pecuniary loss—such as re-auctioning a plot for more than triple the original bid—forfeiture of a substantial deposit is arbitrary and impermissible (Kailash_Nath_Associates_2015, Page 1; Kailash_Nath_Associates_2015, Page 7).

#### 2. Impossibility of Assessing Actual Loss in Public Utility Contracts (*ONGC v. Saw Pipes*, 2003)
- **Genuine Pre-Estimate Exception:** Where contractual terms clearly and unambiguously stipulate liquidated damages (e.g., 1% per week of delay up to 10% ceiling) and the breach involves complex offshore drilling or public utility projects where computing exact actual loss is **impossible or impracticable**, the aggrieved party is not required to prove actual dollar loss before recovering the agreed genuine pre-estimate (ONGC_vs_Saw_Pipes_2003, Page 1; ONGC_vs_Saw_Pipes_2003, Page 14).
- **Burden of Proof:** Once an unambiguous genuine pre-estimate is stipulated in such contracts, the burden shifts to the breaching party to establish that no loss was likely to occur (ONGC_vs_Saw_Pipes_2003, Page 7).

#### 3. Constitutional Baseline on Penalties & Deposits (*Fateh Chand v. Balkishan Das*, 1963)
- **Legal Injury Requirement:** Section 74 dispenses only with proof of the *quantum* of actual loss where assessment is difficult; it does not justify awarding compensation when **no legal injury at all** has resulted from the breach (Fateh_Chand_vs_Balkishan_Das_1963, Page 5).
- **Earnest Money vs. Part-Payment Forfeiture:** While nominal earnest money paid at contract formation may be forfeited upon default, any covenant to forfeit subsequent large part-payments or security deposits operates as a stipulation by way of penalty under the 1899 Amendment and requires proof of loss (Fateh_Chand_vs_Balkishan_Das_1963, Page 9).

Sources: Kailash_Nath_Associates_2015, Page 1; Kailash_Nath_Associates_2015, Page 4; Kailash_Nath_Associates_2015, Page 7; ONGC_vs_Saw_Pipes_2003, Page 1; ONGC_vs_Saw_Pipes_2003, Page 7; ONGC_vs_Saw_Pipes_2003, Page 14; Fateh_Chand_vs_Balkishan_Das_1963, Page 5; Fateh_Chand_vs_Balkishan_Das_1963, Page 9.`,
    citations: [
      {
        case_name: 'Kailash_Nath_Associates_2015',
        page_number: 7,
        snippet: 'Where it is possible to prove actual damage or loss, such proof is not dispensed with, and damage or loss remains a sine qua non for the applicability of Section 74.'
      },
      {
        case_name: 'ONGC_vs_Saw_Pipes_2003',
        page_number: 14,
        snippet: 'If the terms are clear and unambiguous stipulating the liquidated damages in case of the breach of the contract unless it is held that such estimate of damages/compensation is unreasonable or is by way of penalty, party who has committed the breach is required to pay such compensation.'
      },
      {
        case_name: 'Fateh_Chand_vs_Balkishan_Das_1963',
        page_number: 5,
        snippet: 'It merely dispenses with proof of "actual loss or damage"; it does not justify the award of compensation when in consequence of the breach no legal injury at all has resulted.'
      },
      {
        case_name: 'Fateh_Chand_vs_Balkishan_Das_1963',
        page_number: 9,
        snippet: 'The words "to be paid in case of such breach, or if the contract contains any other stipulation by way of penalty" inserted by the 1899 Amendment bring every covenant for forfeiture of deposits or part-payments made subsequent to earnest money within the ambit of Section 74.'
      }
    ],
    stage1_shortlist: [
      {
        case_name: 'Kailash_Nath_Associates_2015',
        display_title: 'Kailash Nath Associates v. Delhi Development Authority',
        citation: '(2015) 4 SCC 136',
        dense_score: 0.92,
        bm25_score: 0.90,
        hybrid_score: 0.91,
        summary: 'Authoritative reconciliation of Section 74 of the Indian Contract Act regarding liquidated damages and forfeiture of earnest money.'
      },
      {
        case_name: 'ONGC_vs_Saw_Pipes_2003',
        display_title: 'Oil & Natural Gas Corporation Ltd. v. Saw Pipes Ltd.',
        citation: '(2003) 5 SCC 705',
        dense_score: 0.89,
        bm25_score: 0.87,
        hybrid_score: 0.88,
        summary: 'Landmark ruling under Section 74 of the Indian Contract Act, 1872 and Section 34 of the Arbitration and Conciliation Act.'
      },
      {
        case_name: 'Fateh_Chand_vs_Balkishan_Das_1963',
        display_title: 'Fateh Chand v. Balkishan Das',
        citation: 'AIR 1963 SC 1405',
        dense_score: 0.85,
        bm25_score: 0.83,
        hybrid_score: 0.84,
        summary: 'Foundational five-judge Constitution Bench decision interpreting Section 74 of the Indian Contract Act, 1872.'
      }
    ],
    stage2_chunks: [
      {
        chunk_id: 'Kailash_Nath_Associates_2015_p7_c0',
        case_name: 'Kailash_Nath_Associates_2015',
        page_number: 7,
        chunk_index: 0,
        text: SEED_LEGAL_CASES[1].pages[2].text,
        word_count: 149,
        dense_score: 0.94,
        bm25_score: 0.91,
        final_score: 0.93,
        passed_floor: true,
        selected_for_prompt: true
      },
      {
        chunk_id: 'ONGC_vs_Saw_Pipes_2003_p14_c0',
        case_name: 'ONGC_vs_Saw_Pipes_2003',
        page_number: 14,
        chunk_index: 0,
        text: SEED_LEGAL_CASES[0].pages[2].text,
        word_count: 152,
        dense_score: 0.91,
        bm25_score: 0.88,
        final_score: 0.90,
        passed_floor: true,
        selected_for_prompt: true
      },
      {
        chunk_id: 'Fateh_Chand_vs_Balkishan_Das_1963_p5_c0',
        case_name: 'Fateh_Chand_vs_Balkishan_Das_1963',
        page_number: 5,
        chunk_index: 0,
        text: SEED_LEGAL_CASES[2].pages[1].text,
        word_count: 89,
        dense_score: 0.87,
        bm25_score: 0.84,
        final_score: 0.86,
        passed_floor: true,
        selected_for_prompt: true
      }
    ],
    dropped_below_floor_count: 1,
    per_case_results: [
      {
        case_name: 'Kailash_Nath_Associates_2015',
        display_title: 'Kailash Nath Associates v. Delhi Development Authority',
        passed_verification: true,
        status: 'VERIFIED',
        answer_section: 'Requires proof of actual loss where possible; dispenses with proof only when assessment is impossible or difficult.',
        citations: [
          { case_name: 'Kailash_Nath_Associates_2015', page_number: 4 },
          { case_name: 'Kailash_Nath_Associates_2015', page_number: 7 }
        ],
        chunks_used: 2
      },
      {
        case_name: 'ONGC_vs_Saw_Pipes_2003',
        display_title: 'Oil & Natural Gas Corporation Ltd. v. Saw Pipes Ltd.',
        passed_verification: true,
        status: 'VERIFIED',
        answer_section: 'Enforces unambiguous genuine pre-estimate of liquidated damages without proof of actual rupee loss where public utility harm cannot be calculated.',
        citations: [
          { case_name: 'ONGC_vs_Saw_Pipes_2003', page_number: 7 },
          { case_name: 'ONGC_vs_Saw_Pipes_2003', page_number: 14 }
        ],
        chunks_used: 2
      },
      {
        case_name: 'Fateh_Chand_vs_Balkishan_Das_1963',
        display_title: 'Fateh Chand v. Balkishan Das',
        passed_verification: true,
        status: 'VERIFIED',
        answer_section: 'Establishes that legal injury is mandatory and covenants forfeiting post-earnest deposits constitute penalties under Section 74.',
        citations: [
          { case_name: 'Fateh_Chand_vs_Balkishan_Das_1963', page_number: 5 },
          { case_name: 'Fateh_Chand_vs_Balkishan_Das_1963', page_number: 9 }
        ],
        chunks_used: 2
      }
    ],
    verification_audit: {
      layer1_citation_match: {
        passed: true,
        has_sources_line: true,
        cited_pairs: [
          { case_name: 'Kailash_Nath_Associates_2015', page_number: 1, exists_in_prompt_chunks: true },
          { case_name: 'Kailash_Nath_Associates_2015', page_number: 4, exists_in_prompt_chunks: true },
          { case_name: 'Kailash_Nath_Associates_2015', page_number: 7, exists_in_prompt_chunks: true },
          { case_name: 'ONGC_vs_Saw_Pipes_2003', page_number: 1, exists_in_prompt_chunks: true },
          { case_name: 'ONGC_vs_Saw_Pipes_2003', page_number: 7, exists_in_prompt_chunks: true },
          { case_name: 'ONGC_vs_Saw_Pipes_2003', page_number: 14, exists_in_prompt_chunks: true },
          { case_name: 'Fateh_Chand_vs_Balkishan_Das_1963', page_number: 5, exists_in_prompt_chunks: true },
          { case_name: 'Fateh_Chand_vs_Balkishan_Das_1963', page_number: 9, exists_in_prompt_chunks: true }
        ],
        details: 'All 8 cited (case_name, page_number) pairs across 3 isolated precedent synthesis blocks deterministically verified.'
      },
      layer1b_body_length: {
        passed: true,
        word_count: 312,
        min_words: 15
      },
      layer2_llm_groundedness: {
        passed: true,
        supported_claims: [
          'Kailash Nath holds that actual loss must be proved where possible and forfeiture is barred when DDA made a windfall on re-auction.',
          'ONGC v. Saw Pipes permits recovery of genuine pre-estimated liquidated damages where public utility loss cannot be calculated.',
          'Fateh Chand distinguishes initial earnest money from subsequent part-payments subject to Section 74 penalty scrutiny.'
        ],
        unsupported_claims: [],
        reasoning: 'Each isolated case holding accurately reflects its respective source passages without cross-attribution or precedent blending.'
      },
      retry_count: 0,
      total_verification_ms: 680
    },
    reranker_enabled: false,
    latency_ms: 1940,
    timestamp: '2026-10-11T08:12:00Z'
  },
  {
    id: 'hist-delaware-veil',
    query: 'What is the standard for piercing the corporate veil in Delaware regarding undercapitalization?',
    requested_mode: 'FAST',
    executed_mode: 'FAST',
    ambiguity: {
      detected: false,
      competing_cases: [],
      score_delta: 0.52,
      threshold: 0.1,
      explanation: 'Single precedent clearly dominates (NetJets_vs_LHC_Delaware_Veil scored 0.93 vs runner-up 0.41; Δ = 0.52 > 0.10).'
    },
    status: 'VERIFIED',
    verified: true,
    answer: `### Answer

Under **Delaware law** (*NetJets Aviation, Inc. v. LHC Communications, LLC* and *Wallace ex rel. Cencom Cable v. Wood*), piercing the corporate or LLC veil under the alter-ego doctrine requires satisfying a strict **two-pronged test** (NetJets_vs_LHC_Delaware_Veil, Page 1):

1. **Prong 1 — Single Economic Entity Analysis:** The court evaluates five factors to determine whether the entity and its owner operated as a single economic unit:
   - Whether the corporation was adequately capitalized for the corporate undertaking (**undercapitalization**);
   - Whether the entity was solvent at the time of the questioned transactions;
   - Whether corporate formalities (dividends, corporate records, functioning officers and directors) were observed;
   - Whether the dominant shareholder siphoned corporate funds; and
   - Whether the corporation functioned simply as a facade for the dominant shareholder (NetJets_vs_LHC_Delaware_Veil, Page 3).
2. **Prong 2 — Mandatory Element of Fraud or Injustice (Undercapitalization Alone is Insufficient):** Under Delaware precedent (*Wallace v. Wood*, 752 A.2d at 1184), **mere undercapitalization or insolvency alone is insufficient** to pierce the corporate veil. Even if an entity is severely undercapitalized at formation or lacks formal board minutes, the plaintiff must prove an **"overall element of injustice or unfairness"** arising from an abuse of the corporate form itself—such as intentionally forming an undercapitalized shell to shield assets while siphoning revenues—rather than merely the underlying breach of contract or unpaid debt (NetJets_vs_LHC_Delaware_Veil, Page 6).

Sources: NetJets_vs_LHC_Delaware_Veil, Page 1; NetJets_vs_LHC_Delaware_Veil, Page 3; NetJets_vs_LHC_Delaware_Veil, Page 6.`,
    citations: [
      {
        case_name: 'NetJets_vs_LHC_Delaware_Veil',
        page_number: 1,
        snippet: 'Delaware courts apply a two-pronged alter-ego test requiring the plaintiff to demonstrate both (1) that the corporation and its shareholders operated as a "single economic entity," and (2) that the corporate form was used to sanction a fraud, promote injustice, or evade a legal obligation.'
      },
      {
        case_name: 'NetJets_vs_LHC_Delaware_Veil',
        page_number: 3,
        snippet: 'In evaluating the first prong—whether the entity operated as a single economic unit—Delaware courts examine five primary factors: (a) whether the corporation was adequately capitalized for the corporate undertaking (undercapitalization)...'
      },
      {
        case_name: 'NetJets_vs_LHC_Delaware_Veil',
        page_number: 6,
        snippet: 'Crucially, under Delaware precedent (Wallace v. Wood, 752 A.2d at 1184), mere undercapitalization or insolvency alone is insufficient to pierce the corporate veil... the plaintiff must satisfy the second prong by proving an "overall element of injustice or unfairness."'
      }
    ],
    stage1_shortlist: [
      {
        case_name: 'NetJets_vs_LHC_Delaware_Veil',
        display_title: 'NetJets Aviation, Inc. v. LHC Communications, LLC (Delaware Veil Piercing)',
        citation: '537 F.3d 168 & 752 A.2d 1175',
        dense_score: 0.94,
        bm25_score: 0.91,
        hybrid_score: 0.93,
        summary: 'Establishes the two-pronged Delaware standard for piercing the corporate veil under the alter-ego doctrine.'
      }
    ],
    stage2_chunks: [
      {
        chunk_id: 'NetJets_vs_LHC_Delaware_Veil_p1_c0',
        case_name: 'NetJets_vs_LHC_Delaware_Veil',
        page_number: 1,
        chunk_index: 0,
        text: SEED_LEGAL_CASES[3].pages[0].text,
        word_count: 93,
        dense_score: 0.92,
        bm25_score: 0.89,
        final_score: 0.91,
        passed_floor: true,
        selected_for_prompt: true
      },
      {
        chunk_id: 'NetJets_vs_LHC_Delaware_Veil_p3_c0',
        case_name: 'NetJets_vs_LHC_Delaware_Veil',
        page_number: 3,
        chunk_index: 0,
        text: SEED_LEGAL_CASES[3].pages[1].text,
        word_count: 101,
        dense_score: 0.95,
        bm25_score: 0.92,
        final_score: 0.94,
        passed_floor: true,
        selected_for_prompt: true
      },
      {
        chunk_id: 'NetJets_vs_LHC_Delaware_Veil_p6_c0',
        case_name: 'NetJets_vs_LHC_Delaware_Veil',
        page_number: 6,
        chunk_index: 0,
        text: SEED_LEGAL_CASES[3].pages[2].text,
        word_count: 108,
        dense_score: 0.96,
        bm25_score: 0.93,
        final_score: 0.95,
        passed_floor: true,
        selected_for_prompt: true
      }
    ],
    dropped_below_floor_count: 0,
    verification_audit: {
      layer1_citation_match: {
        passed: true,
        has_sources_line: true,
        cited_pairs: [
          { case_name: 'NetJets_vs_LHC_Delaware_Veil', page_number: 1, exists_in_prompt_chunks: true },
          { case_name: 'NetJets_vs_LHC_Delaware_Veil', page_number: 3, exists_in_prompt_chunks: true },
          { case_name: 'NetJets_vs_LHC_Delaware_Veil', page_number: 6, exists_in_prompt_chunks: true }
        ],
        details: 'All 3 cited (case_name, page_number) pairs deterministically matched prompt chunks.'
      },
      layer1b_body_length: {
        passed: true,
        word_count: 196,
        min_words: 15
      },
      layer2_llm_groundedness: {
        passed: true,
        supported_claims: [
          'Delaware applies a two-pronged alter-ego test requiring single economic entity status plus fraud or injustice.',
          'Five factors govern the single economic entity prong, including undercapitalization, solvency, formalities, and siphoning.',
          'Mere undercapitalization alone is insufficient under Wallace v. Wood without an independent abuse of the corporate form.'
        ],
        unsupported_claims: [],
        reasoning: 'All assertions directly trace to Pages 1, 3, and 6 of NetJets_vs_LHC_Delaware_Veil.'
      },
      retry_count: 0,
      total_verification_ms: 390
    },
    reranker_enabled: false,
    latency_ms: 1120,
    timestamp: '2026-10-11T08:14:00Z'
  },
  {
    id: 'hist-chevron-insufficient',
    query: 'Standard for Chevron agency deference following Loper Bright Enterprises v. Raimondo',
    requested_mode: 'AUTO',
    executed_mode: 'FAST',
    auto_routing_reason: 'All candidate cases scored below the 0.40 Self-RAG relevance floor.',
    ambiguity: {
      detected: false,
      competing_cases: [],
      score_delta: 0.02,
      threshold: 0.1,
      explanation: 'No uploaded cases met the minimum 0.40 relevance threshold for administrative deference.'
    },
    status: 'INSUFFICIENT',
    verified: false,
    answer: 'No verified answer could be found in the uploaded documents for this question.',
    citations: [],
    stage1_shortlist: [
      {
        case_name: 'Kailash_Nath_Associates_2015',
        display_title: 'Kailash Nath Associates v. Delhi Development Authority',
        citation: '(2015) 4 SCC 136',
        dense_score: 0.24,
        bm25_score: 0.11,
        hybrid_score: 0.19,
        summary: 'Authoritative reconciliation of Section 74 of the Indian Contract Act regarding liquidated damages.'
      }
    ],
    stage2_chunks: [
      {
        chunk_id: 'Kailash_Nath_Associates_2015_p1_c0',
        case_name: 'Kailash_Nath_Associates_2015',
        page_number: 1,
        chunk_index: 0,
        text: SEED_LEGAL_CASES[1].pages[0].text,
        word_count: 92,
        dense_score: 0.22,
        bm25_score: 0.08,
        final_score: 0.17,
        passed_floor: false,
        selected_for_prompt: false
      }
    ],
    dropped_below_floor_count: 3,
    verification_audit: {
      layer1_citation_match: {
        passed: false,
        has_sources_line: false,
        cited_pairs: [],
        details: 'Self-RAG Grader rejected all candidate chunks (max score 0.17 < 0.40 relevance floor). Fail-closed fallback triggered.'
      },
      layer1b_body_length: {
        passed: false,
        word_count: 14,
        min_words: 15
      },
      layer2_llm_groundedness: {
        passed: false,
        supported_claims: [],
        unsupported_claims: [],
        reasoning: 'No chunks passed the 0.40 Self-RAG relevance floor; system failed closed per FR-2.4 and FR-3.4.'
      },
      retry_count: 0,
      total_verification_ms: 95
    },
    reranker_enabled: false,
    latency_ms: 340,
    timestamp: '2026-10-11T08:15:00Z'
  }
];
