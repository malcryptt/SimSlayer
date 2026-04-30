# SimSlayer
> Adversarial prompt injection bot for the Simcluster $25K tournament

Written by mal4crypt

## ⚠ Before You Start
- You need X API Basic plan ($100/mo) — free tier is too limited
- Use a throwaway X account, NOT your main account
- Read the full Simcluster competition rules before running
- Start slow — let the tracker find best payloads before scaling

## Setup
1. pip install -r requirements.txt
2. python main.py
3. Enter X API credentials
4. Set keywords, adjust intervals, hit Start

## How It Works
SimSlayer scans X for threads where AI bots are active, scores 
accounts for bot likelihood, fires prompt injection payloads as 
replies, then tracks which techniques successfully trigger the 
target phrase. Success-weighted payload rotation means it gets 
smarter over time.

## Architecture
- GUI: CustomTkinter light theme, SaaS dashboard style
- Engine: Threaded bot loop, rate-limit safe  
- Injection: 8 technique categories, success-weighted
- Tracking: SQLite, full shot history + payload analytics
- Export: CSV + TXT session reports for competition receipts
