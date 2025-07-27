# CODERECET

## Project Repository
*Commit and save your changes here*

### Team Name : 404-notfound
### Team Members : Adarsh abhraham johnson,Amith Paul Siju,A,Arvin Joseph
### Project Description: 
The Loop is a Web3-enabled digital ecosystem designed to bridge the communication gap between the youth and the government in Kerala, India. It leverages the power of Generative AI to make governance accessible and a blockchain to make civic participation transparent and rewarding.

🎯 The Problem
In Kerala, a generation of bright, ambitious young people has powerful ideas to shape the future, but their voices often get lost in complex bureaucratic systems. This creates a "participation gap" fueled by two core issues:

For Citizens: Government schemes are often buried in dense, hard-to-understand documents, creating a barrier to access. Traditional feedback channels feel like black holes, leading to cynicism and disengagement.

For Government: Officials receive a high volume of unstructured feedback through chaotic channels (email, social media), making it impossible to identify key trends and public priorities effectively.

✨ The Solution: "The Loop"
"The Loop" is not just an app; it's a dedicated digital ecosystem built to empower the youth of Kerala by turning their frustration into action. It creates a virtuous cycle where informed citizens submit high-quality ideas, and officials receive clear, data-driven insights to create more effective policy.

The platform is built on two interconnected wings:

💡 1. The Information Wing
This is an intelligent AI-powered guide that demystifies complex government schemes.

AI-Powered Q&A: Users can ask questions in simple Malayalam or English about any government scheme loaded into our knowledge base.

RAG (Retrieval-Augmented Generation): The AI provides clear, accurate answers based only on official, source-verified PDF documents, eliminating misinformation.

Accessibility: An informed youth is a confident youth. This wing provides the knowledge necessary for meaningful civic engagement.

🚀 2. The Innovation Wing
This is the direct line for citizens to contribute their ideas and solutions.

AI-Powered Submission: Users can submit ideas in any format (text, voice, images). An AI co-pilot helps them structure their proposals and provides real-time suggestions by cross-referencing the Information Wing's knowledge base.

AI-Powered Analysis: For officials, the AI automatically generates a summary, relevant tags (e.g., #Environment, #Education), and a sentiment analysis (Positive/Negative/Neutral) for every single submission.

Officials' Dashboard: All submitted ideas are displayed on a clean dashboard, transforming unstructured public feedback into a prioritized, data-driven command center.

🔗 Web3 Integration: The Future is Decentralized & Transparent
To guarantee that a user's voice is never silenced, altered, or ignored, "The Loop" is built for a Web3 future.

NFTs for Contribution (ERC721): Every idea submitted successfully mints a unique NFT to the contributor's wallet. This provides immutable, on-chain proof of their contribution and ownership.

"The Loop Token" for Rewards (ERC20): High-quality ideas that are upvoted by the community or selected by officials are rewarded with $LOOP tokens. This creates a tangible incentive for valuable participation.

Decentralized Voting: The platform features a community voting system. Ideas are sorted by vote count on the dashboard, allowing the best ideas, as judged by the people, to rise to the top.

## Technical Details

### Technologies/Components Used

## For Software:

Languages used: Python, Solidity, JavaScript (for the planned frontend)

Frameworks used: Streamlit (for the PoC), Hardhat (for blockchain development)

Libraries used:

Python: Together.ai, web3.py, PyPDF2

JavaScript/Solidity: @openzeppelin/contracts, ethers.js (via Hardhat)

Tools used:

IDE: Visual Studio Code

Version Control: Git & GitHub

Local Blockchain: Ganache

Package Managers: pip (for Python), npm (for Node.js/Hardhat)

Deployment & DevOps:

Containerization: Docker

Cloud Platform: Amazon Web Services (AWS)

## Implementation

## For Software:

### Installation
Clone the repository:

git clone [https://github.com/your-username/the-loop-project.git](https://github.com/amithpaul/CODERECET_THELOOP.git)
cd the-loop-project
Install Python dependencies:

pip install -r requirements.txt
Install Smart Contract dependencies:

cd hardhat_project
npm install
cd ..


### Run
Start your local blockchain (Ganache): Open the Ganache application on your computer.

Deploy the smart contracts:

cd hardhat_project
npx hardhat run scripts/deploy.js --network ganache
npx hardhat run scripts/deploy_token.js --network ganache
cd ..
Run the main web application:

streamlit run app.py

### Project Documentation

### Screenshots (Add at least 3)

### Diagrams

Caption: This diagram illustrates the complete workflow of "The Loop" ecosystem.

A Citizen starts at the Homepage and chooses to enter either the Information or Innovation Wing.

In the Information Wing, the user's question is sent to the AI Engine (Gemini), which uses a knowledge base to generate a factual, grounded answer that is displayed back to the user.

In the Innovation Wing, the user's idea is sent to the AI Engine for analysis (summarization, tagging, and sentiment). Upon submission, a request is sent to the Blockchain to mint an NFT as proof of contribution.

The analyzed idea is then displayed on the Officials' Dashboard, where community members can vote and officials can review insights and award Loop Tokens by interacting with the smart contracts.


[View Our Workflow Diagram](https://drive.google.com/file/d/1122-9lGUxz3NzqaEFgbRkBA4BO954bfF/view?usp=drive_link)




### Project Demo

### Video
[Add your demo video link here] Explain what the video demonstrates

## Additional Demos
[Add any extra demo materials/links]

## Team Contributions
[Adarsh Abraham Johnson]: [ Implimented Web3 and Agentic AI parts ]
[Amith Paul Siju]: [Implimented Devop, ML and Deployment parts]
[Arvin Joseph]: [Frontend Implementations and design parts]
[Arjun T Aghilesh]: [Frontend Implementations and design parts]

