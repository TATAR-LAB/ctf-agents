SUNY AI Platform Final Report
Field Value
Name:
Email:
Project Name: Advancing LLM-Based CTF Solving with D-CIPHER
Project ID: alb-prj-utatar-sbx

1. Tools and Services Used on Google Cloud Platform
   • Google Compute Engine
   • Vertex AI
   o Open Source Model Deployments
   o Gemini Model Access (for Gemini 3 Pro and Gemini 3 Flash model access)
   o Jupyter Workbenches
   • Cloud Storage (for experiment logs and results)

2. Research Team Members
   • Dr. Unal Tatar
   • Hakan T. Otal
   • Joseph M. Escobar
   • Tyler H. Merves
   • Michael H. Conaway
   CEHC, University at Albany, SUNY

3. Narrative
   a) Impact of the SUNY AI Platform on Our Work
   Our project, "Advancing LLM-Based CTF Solving with D-CIPHER," systematically evaluated how large language model (LLM) agents can autonomously solve Capture The Flag (CTF) cybersecurity challenges. Access to the SUNY AI Platform was critical to our research — it provided the GPU-equipped compute infrastructure and Vertex AI API access needed to run large-scale experiments across 200 CTF challenges from the NYU CTF Bench. Without the platform, we could not have benchmarked 10+ frontier LLMs or executed our various testing environment configurations, prompt strategies, and auto-prompting approaches. Our best configuration achieved a 52% solve rate (104/200 challenges), advancing the state-of-the-art for automated CTF solving.
   b) Impact on the Field
   Our research contributes to the growing field of AI-assisted cybersecurity by providing: (1) the first systematic comparison of frontier and specialized LLMs on a standardized CTF benchmark, (2) evidence that enhanced security tooling provides modest but meaningful improvement (+5% absolute solve rate) over baseline environments, (3) cost-performance analysis showing that Gemini 3 Flash offers the best cost-per-solve ratio ($0.05 vs. $0.44 for Gemini 3 Pro), and (4) insights into multi-agent architecture design for cybersecurity tasks.
   c) Continuation Plans
   We plan to continue this research by expanding to the CyBench benchmark (90 additional challenges), completing our multi-agent architecture comparisons, and conducting reproducibility analysis. We would welcome the opportunity to continue using the SUNY AI Platform for this work, as the Vertex AI integration and compute resources are central to our experimental pipeline.

4. Grants Already Submitted
   • [If applicable: Funding Agency, Name of Solicitation, Submission/Due Date]
   • [VICEROY?]

5. Grants Planned or In Progress
   • [If applicable: Funding Agency, Name of Solicitation, Due Date]

6. Publications
   • Paper submission — "Systematic Capability Benchmarking of Frontier Large Language Models for Offensive Cyber Tasks", SIEDS 2026

7. Conference Submissions
   • Poster presentation — " When AI Transforms Cyber Operations: Evaluating Agentic LLM Capabilities", VICEROY Symposium 2026
   • Talk presentation — "Advancing LLM-Based CTF Solving with D-CIPHER: A Systematic Evaluation of Models, Environments, and Architectures", NTIR 2026
   • Paper submission — "Systematic Capability Benchmarking of Frontier Large Language Models for Offensive Cyber Tasks", SIEDS 2026

---

---

Draft Responses for the SUNY AI Platform Project Wrap Up Form
Deadline: March 13, 2026

Question 1: Name

Question 2: Project ID
alb-prj-utatar-sbx

Question 3: Email (for follow-up questions)

>

Question 4: Narrative Report
Research Team
• Dr. Unal Tatar
• Hakan T. Otal
• Joseph M. Escobar
• Tyler H. Merves
• Michael H. Conaway
CEHC, University at Albany, SUNY

> Tools and Services Used on Google Cloud Platform
> • Google Compute Engine
> • Vertex AI
> o Open Source Model Deployments
> o Gemini Model Access (for Gemini 3 Pro and Gemini 3 Flash model access)
> o Jupyter Workbenches
> • Cloud Storage (for experiment logs and results) > >
> Impact of SUNY AI Platform on Our Work: Our project, "Advancing LLM-Based CTF Solving with D-CIPHER," systematically evaluated how large language model (LLM) agents can autonomously solve Capture The Flag (CTF) cybersecurity challenges. Access to the SUNY AI Platform was critical to our research — it provided the GPU-equipped compute infrastructure and Vertex AI API access needed to run large-scale experiments across 200 CTF challenges from the NYU CTF Bench. Without the platform, we could not have benchmarked 10+ frontier LLMs or executed our various testing environment configurations, prompt strategies, and auto-prompting approaches. Our best configuration achieved a 52% solve rate (104/200 challenges), advancing the state-of-the-art for automated CTF solving.
> Impact on the Field: Our research contributes to the growing field of AI-assisted cybersecurity by providing: (1) the first systematic comparison of frontier and specialized LLMs on a standardized CTF benchmark, (2) evidence that enhanced security tooling provides modest but meaningful improvement (+5% absolute solve rate) over baseline environments, (3) cost-performance analysis showing that Gemini 3 Flash offers the best cost-per-solve ratio ($0.05 vs. $0.44 for Gemini 3 Pro), and (4) insights into multi-agent architecture design for cybersecurity tasks.
> Continuation Plans: We plan to continue this research by expanding to the CyBench benchmark (90 additional challenges), completing our multi-agent architecture comparisons, and conducting reproducibility analysis. We would welcome the opportunity to continue using the SUNY AI Platform for this work, as the Vertex AI integration and compute resources are central to our experimental pipeline.
> Grant Applications:
> • [If applicable: Funding Agency, Name of Solicitation, Submission/Due Date]
> • [VICEROY]
> Publications:
> • Poster presentation — " When AI Transforms Cyber Operations: Evaluating Agentic LLM Capabilities", VICEROY Symposium 2026
> • Talk presentation — "Advancing LLM-Based CTF Solving with D-CIPHER: A Systematic Evaluation of Models, Environments, and Architectures", NTIR 2026
> • Paper submission — "Systematic Capability Benchmarking of Frontier Large Language Models for Offensive Cyber Tasks", SIEDS 2026

Question 5: Would you use the SUNY AI Platform if your participation required some financial contribution?
Yes

Question 6: If you answered Yes for #5, please briefly explain why, or any conditions to that Yes?
The SUNY AI Platform provided essential access to Vertex AI and compute infrastructure that would otherwise cost thousands of dollars through commercial cloud providers. Our total experiment costs exceeded $150 in API credits alone across all model benchmarks, plus significant compute time for Docker-based challenge execution. A cost-sharing model would still be significantly more affordable than commercial alternatives, provided the contribution remains reasonable relative to a typical research budget (e.g., under $500/semester). The centralized infrastructure, workforce identity federation, and pre-configured GCP access also saved significant setup time compared to managing individual cloud accounts.

Question 7: How were you able to access compute and storage for research previously?
• Supported through my campus offerings
• Funded out of my own pocket (if you used personal OpenRouter/API credits)
• Supported through shared SUNY system and/or state offerings

Question 8: Please briefly explain your answer for #7.
Previously, I relied on campus-provided computing resources and personal API credits for smaller-scale LLM experiments. However, campus resources lacked the Vertex AI integration and GPU-equipped instances needed for large-scale multi-agent experiments. For API access to proprietary models (OpenAI, Anthropic), I used personal or lab funding through services like OpenRouter. The SUNY AI Platform was the first resource that provided integrated GCP access with Vertex AI at a scale sufficient for systematic benchmarking of 200 CTF challenges across multiple model configurations.

Question 9: If you have not used high performance computing in the past, what stopped you?
Cost

Question 10: If you didn't have access to the SUNY AI Platform, which resources would you have leveraged?
Without the SUNY AI Platform, we would have relied on a combination of: (1) OpenRouter API credits purchased with personal/lab funds for model access, (2) local machines with consumer GPUs for running open-source models via Ollama, and (3) free-tier cloud credits (e.g., Google Cloud free trial). However, these alternatives would have severely limited our experimental scope — we would not have been able to benchmark as many models or run the full 200-challenge suite across multiple configurations. The research would have taken significantly longer and produced less comprehensive results.

Question 11: If you weren't able to use all the credits you originally applied for, please explain why.
We utilized the majority of our allocated credits for running experiments across our five research questions. The primary costs came from Vertex AI API calls (Gemini 3 Pro experiments totaled ~$42 per full 200-challenge run) and Compute Engine instance hours. Some credits may remain unused because: (1) several planned experiments (RQ4 architecture comparisons, RQ5 reproducibility with 5 replications) could not be fully completed within the project timeline, and (2) we optimized our experimental pipeline to reduce costs by using Gemini 3 Flash ($2.69/run) for preliminary testing before committing to more expensive Gemini 3 Pro runs.

Question 12: Did the SUNY AI Platform advance your research in any of the following ways?
Select:
• Advanced my research to enhance a conference submission
• Completed a component of my research (describe in the next question)
• Advanced my research so that I could publish

Question 13: Please describe your response above briefly.
The SUNY AI Platform enabled us to complete the experimental component of our research on LLM-based CTF solving. Specifically, we completed a comprehensive benchmark of frontier LLMs across 200 cases, tested the impact of Kali Linux security tooling vs. Ubuntu baseline environments, and analyzed prompt engineering strategies — all resulting in a poster presentation. The platform's Vertex AI access was essential for running Gemini 3 Pro and Flash models, which emerged as the top-performing and most cost-effective models respectively. These results directly supported our conference poster submission and provide a foundation for a future journal publication.

Question 14: Do you have any feedback on your experience with the platform?
Onboarding: The onboarding process was straightforward. The workforce identity federation setup worked well for authentication, though initial documentation on how to configure Vertex AI API access for specific model endpoints could be more detailed.
Using the Platform: The platform performed reliably for our compute-intensive workloads. Running Docker containers on Compute Engine instances worked seamlessly, and Vertex AI provided stable access to Gemini models. One area for improvement would be clearer documentation on billing/credit usage monitoring so researchers can better plan their experiments against their budget.
Off-boarding: The project wrap-up form is comprehensive and easy to fill out. It would be helpful if there were a dashboard showing cumulative credit/resource usage to reference when completing the narrative report.
Overall, the SUNY AI Platform was a valuable resource that directly enabled research we could not have conducted otherwise. We would enthusiastically participate in future rounds of the program.

---

---

Draft Responses for the SUNY AI Platform: Extension Request Form
Deadline: March 18, 2026

Question 1: Name (First and Last)

>

Question 2: Project ID
alb-prj-utatar-sbx

Question 3: Email (for follow up questions)

>

Question 4: Please provide a list of tools and services used on Google Cloud Platform you will need to continue your project. Include an estimate of required services, cost, and duration needed.

We plan to use the following GCP tools and services for the extension period (approximately 6–9 months):

• Google Compute Engine — GPU-equipped VM instances (e.g., n1-standard-8 with NVIDIA T4/A100) for running Docker-based CTF challenge environments and hosting open-source model inference. Estimated cost: ~$8,000–$12,000 (based on ~1,500–2,000 GPU-hours at $5–$6/hr for T4 instances).

• Vertex AI — API access for Gemini 3 Pro and Gemini 3 Flash models for agent benchmarking across multiple datasets and configurations. Estimated cost: ~$15,000–$20,000 (based on projected experimental runs across 200+ CTF challenges, 90 CyBench challenges, and new AI safety/security datasets with multiple model configurations and replications).

• Vertex AI — Open-source model deployment endpoints for deploying and evaluating open-source LLMs (e.g., Llama, Mistral, Qwen, DeepSeek) on Vertex AI endpoints. Estimated cost: ~$5,000–$8,000.

• Vertex AI Jupyter Workbenches — For interactive data analysis, visualization, and experiment monitoring. Estimated cost: ~$1,000–$2,000.

• Cloud Storage — For storing experiment logs, results, model artifacts, and datasets. Estimated cost: ~$500–$1,000.

Total estimated budget: ~$30,000–$43,000 in GCP credits over 6–9 months. We are requesting $50,000 to provide a buffer for additional experiments, replications, and unexpected compute needs.

Question 5: Please provide a 1-2 paragraph justification for the extension. Be clear about which research goals will be accomplished with more time on the platform.

Our initial project on the SUNY AI Platform produced significant results — we benchmarked 10+ frontier LLMs on 200 CTF challenges, achieving a 52% solve rate with our best configuration and generating data for one paper submission (SIEDS 2026), a poster presentation (VICEROY Symposium 2026), and a talk presentation (NTIR 2026). However, several planned research questions remain incomplete: our multi-agent architecture comparisons (RQ4), reproducibility analysis with 5 replications per configuration (RQ5), and expansion to the CyBench benchmark (90 additional challenges) were not completed within the original timeline. With extended access, we will complete these experiments, test new architectures such as asymmetric planner/executor setups and knowledge-augmented retrieval (RAG) pipelines, and begin exploring how these LLM agent frameworks can be applied to AI safety and security research by evaluating them on diverse cybersecurity datasets beyond CTF challenges.

Extending our access will enable us to pivot toward an important emerging direction: systematically evaluating LLM agents' capabilities and limitations in adversarial security contexts, which directly informs AI safety research. We plan to run experiments across various established security datasets and benchmarks to characterize where LLM agents succeed and fail in offensive and defensive cybersecurity tasks. This extension will support the production of at least 2–3 additional publications, including a journal paper on comprehensive model benchmarking, a conference paper on multi-agent architecture optimization for cybersecurity, and a paper on AI safety implications of LLM-based security tools. The SUNY AI Platform's Vertex AI integration and GPU compute infrastructure remain essential for this work, as commercial alternatives would cost significantly more and lack the centralized access our team relies on.

Question 6: How will you fund use of the platform resources? Use of the SUNY AI Platform will require some cost-sharing after March 18.

We are prepared to support cost-sharing for continued platform use through a combination of funding sources. Our lab currently has allocated research funds that can contribute to GCP costs, and we are actively pursuing external grant applications to secure dedicated funding for this line of research. Additionally, we have demonstrated cost-conscious experiment design in our initial project — for example, using Gemini 3 Flash ($2.69 per full 200-challenge run) for preliminary testing before scaling to more expensive models like Gemini 3 Pro ($42 per run). We will continue these cost optimization practices to maximize the value of platform credits. Our team is also exploring industry partnerships and university-sponsored computing grants that could supplement the cost-sharing requirement. We anticipate being able to contribute a reasonable share of costs provided the contribution remains proportionate to a typical academic research budget.


---
---


Feedback

How the platform supported our research:

1. Vertex AI access was the single most impactful resource for our project. It allowed us to benchmark Gemini 3 Pro and Gemini 3 Flash models side-by-side against other frontier LLMs (GPT, Claude, DeepSeek, Grok) in a controlled, reproducible environment. Without the platform, we would have had to manage separate API accounts and billing across multiple cloud providers, which would have fragmented our experimental pipeline and made fair comparisons far more difficult. The pre-configured GCP access and easy to use JupyterLab Workbenches meant our five-person research team could focus on the science rather than cloud infrastructure setup.

2. Additionally, the JupyterLab Workbenches enabled us to run Docker-based CTF challenge environments at scale — something that was not feasible on our campus computing resources. Each experimental run involved spinning up isolated Docker containers (both Ubuntu and Kali Linux) for 200 CTF challenges, which required sustained compute over many hours. The platform's reliability during these long-running batch experiments was critical; we could launch overnight runs and trust they would complete without interruption.

Publications and outcomes:
• Paper submission — "Systematic Capability Benchmarking of Frontier Large Language Models for Offensive Cyber Tasks," SIEDS 2026
• Poster presentation — "When AI Transforms Cyber Operations: Evaluating Agentic LLM Capabilities," VICEROY Symposium 2026
• Talk presentation — "Advancing LLM-Based CTF Solving with D-CIPHER: A Systematic Evaluation of Models, Environments, and Architectures," NTIR 2026

Anecdote: One of the most surprising findings from our work on the platform came from the cost analysis. We had expected the most expensive models to be the best performers, but our Vertex AI experiments revealed that Gemini 3 Flash — at just $0.05 per solved challenge — actually matched or outperformed several models that cost 8–10x more per solve. This insight only emerged because the platform gave us the scale to run comprehensive benchmarks across 10+ models on all 200 challenges. Had we been constrained to a few models on personal credits, we would have missed this cost-performance finding entirely, and it became one of the key contributions in our paper submission.

---
---
