#!/usr/bin/env python3
"""Build the Morning Shelf HTML index from all paper sources."""

import json
import os
import re
import subprocess
from datetime import datetime, timezone

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(SCRIPT_DIR, "acolyer_data.json")
OUTPUT_FILE = os.path.join(SCRIPT_DIR, "index.html")

# ============================================================
# SOURCE 1: Adrian Colyer's The Morning Paper (already scraped)
# ============================================================
with open(DATA_FILE) as f:
    acolyer = json.load(f)

# ============================================================
# SOURCE 2: Marc Brooker's Essential Reading Lists
# ============================================================

BROOKER_LISKOV = [
    ("Data abstraction and hierarchy", "Barbara Liskov", "1987", "Foundational paper on abstract data types and the Liskov Substitution Principle", "https://dl.acm.org/doi/10.1145/62138.62141"),
    ("A behavioral notion of subtyping", "Barbara Liskov, Jeannette Wing", "1994", "Formal definition of behavioral subtyping — the 'L' in SOLID", "https://dl.acm.org/doi/10.1145/197320.197383"),
    ("Behavioral subtyping using invariants and constraints", "Barbara Liskov, Jeannette Wing", "1999", "Refinement of behavioral subtyping with invariants", "https://link.springer.com/chapter/10.1007/3-540-48118-4_18"),
    ("Viewstamped Replication: A New Primary Copy Method to Support Highly Available Distributed Systems", "Brian Oki, Barbara Liskov", "1988", "One of the earliest consensus protocols, predates Paxos", "https://dl.acm.org/doi/10.1145/62546.62549"),
    ("Viewstamped Replication Revisited", "Barbara Liskov, James Cowling", "2012", "Modern, clearer description of Viewstamped Replication", "http://pmg.csail.mit.edu/papers/vr-revisited.pdf"),
    ("Practical Byzantine fault tolerance", "Miguel Castro, Barbara Liskov", "1999", "First practical implementation of Byzantine fault tolerance", "http://pmg.csail.mit.edu/papers/osdi99.pdf"),
    ("Byzantine clients rendered harmless", "Rodrigo Rodrigues, Barbara Liskov", "2005", "Strengthening BFT protocols against client misbehavior", "https://pmg.csail.mit.edu/papers/bft-harmless.pdf"),
]

BROOKER_LAMPORT = [
    ("A New Solution of Dijkstra's Concurrent Programming Problem", "Leslie Lamport", "1974", "The Bakery algorithm — mutual exclusion without hardware support", "https://dl.acm.org/doi/10.1145/361179.361202"),
    ("Time, Clocks and the Ordering of Events in a Distributed System", "Leslie Lamport", "1978", "Logical clocks, happened-before relation, replicated state machines — 8000+ citations", "https://dl.acm.org/doi/10.1145/359545.359563"),
    ("Distributed Snapshots: Determining Global States of a Distributed System", "K. Mani Chandy, Leslie Lamport", "1985", "The Chandy-Lamport snapshot algorithm", "https://dl.acm.org/doi/10.1145/214451.214456"),
    ("What Good Is Temporal Logic?", "Leslie Lamport", "1983", "Philosophy and practice of temporal logic for specifying concurrent systems", "https://dl.acm.org/doi/10.5555/1624056.1624060"),
    ("The Part-Time Parliament", "Leslie Lamport", "1998 (submitted 1990)", "The original Paxos consensus algorithm paper — famously told as a parable of ancient Greece", "https://dl.acm.org/doi/10.1145/279227.279229"),
    ("Paxos Made Simple", "Leslie Lamport", "2001", "Simplified, more accessible explanation of the Paxos algorithm", "https://lamport.azurewebsites.net/pubs/paxos-simple.pdf"),
    ("The Byzantine Generals Problem", "Leslie Lamport, Robert Shostak, Marshall Pease", "1982", "Foundational paper on Byzantine fault tolerance in distributed systems", "https://dl.acm.org/doi/10.1145/357172.357176"),
    ("The Implementation of Reliable Distributed Multiprocess Systems", "Leslie Lamport", "1978", "Expands on replicated state machines from Time, Clocks paper", "https://dl.acm.org/doi/10.5555/889804"),
]

BROOKER_LYNCH = [
    ("A Hundred Impossibility Proofs for Distributed Computing", "Nancy Lynch", "1989", "Massive survey of impossibility results across distributed systems — 103 references", "https://dl.acm.org/doi/10.1145/72981.72982"),
    ("Brewer's conjecture and the feasibility of consistent, available, partition-tolerant web services", "Seth Gilbert, Nancy Lynch", "2002", "Formal proof of the CAP theorem", "https://dl.acm.org/doi/10.1145/564585.564601"),
    ("Consensus in the Presence of Partial Synchrony", "Cynthia Dwork, Nancy Lynch, Larry Stockmeyer", "1988", "One of three foundational consensus solutions from the 1980s", "https://dl.acm.org/doi/10.1145/42282.42283"),
    ("Impossibility of distributed consensus with one faulty process", "Michael Fischer, Nancy Lynch, Michael Paterson", "1985", "The FLP result — no asynchronous consensus protocol can tolerate even one failure", "https://dl.acm.org/doi/10.1145/3149.214121"),
    ("Reaching approximate agreement in the presence of faults", "Danny Dolev, Nancy Lynch et al.", "1986", "When exact consensus is impossible, how close can you get?", "https://dl.acm.org/doi/10.1145/5925.5931"),
]

# ============================================================
# SOURCE 3: Papers We Love Videos (scraped from paperswelove.org/videos/)
# ============================================================

PWL_VIDEOS = [
    ("Dynamo: Amazon's Highly Available Key-Value Store", "Corrina Sivak", "PWL Tokyo", "2026-05-07", "https://paperswelove.org/videos/"),
    ("Zep: A Temporal Knowledge Graph Architecture for Agent Memory", "Rylan Talerico", "PWL NYC", "2025-12-07", "https://paperswelove.org/videos/"),
    ("EXE: Automatically Generating Inputs of Death", "Michael Vaughn", "PWL NYC", "2025-10-28", "https://paperswelove.org/videos/"),
    ("Apache Arrow DataFusion", "Alex Kesling", "PWL NYC", "2025-02-12", "https://paperswelove.org/videos/"),
    ("Error Detecting and Error Correcting Codes", "Yotam Bentov", "PWL NYC", "2024-12-13", "https://paperswelove.org/videos/"),
    ("Liquid Type Systems", "Nathan Taylor", "PWL NYC", "2024-11-22", "https://paperswelove.org/videos/"),
    ("Bin packing can be solved within 1 + ε in linear time", "Yiduo Ke", "PWL NYC", "2024-08-30", "https://paperswelove.org/videos/"),
    ("Attention Is All You Need", "Eric Leung", "PWL NYC", "2024-07-16", "https://paperswelove.org/videos/"),
    ("An Introduction to Bε-trees and Write-Optimization", "Ori Bernstein", "PWL NYC", "2023-06-21", "https://paperswelove.org/videos/"),
    ("Zanzibar: Google's Consistent, Global Authorization System", "Jake Moshenko", "PWL NYC", "2021-07-29", "https://paperswelove.org/videos/"),
    ("Toward a Generic Fault Tolerance Technique", "Michael Pigott", "PWL NYC", "2021-06-10", "https://paperswelove.org/videos/"),
    ("The Demikernel and the Future of Kernel-Bypass Systems", "Irene Zhang", "PWL SF", "2021-02-25", "https://paperswelove.org/videos/"),
    ("CRaft: An Erasure-coding-supported Version of Raft", "Toma Morris", "PWL NYC", "2020-09-03", "https://paperswelove.org/videos/"),
    ("Understanding Real-World Concurrency Bugs in Go", "David Ashby", "PWL NYC", "2020-07-22", "https://paperswelove.org/videos/"),
    ("Build Systems a la Carte", "Dan Bentley", "PWL NYC", "2020-05-30", "https://paperswelove.org/videos/"),
    ("Deny Capabilities for Safe, Fast Actors", "Sean T. Allen", "PWL NYC", "2020-01-17", "https://paperswelove.org/videos/"),
    ("Life Beyond Distributed Transactions", "PWL NYC", "PWL NYC", "2020-01-03", "https://paperswelove.org/videos/"),
    ("Space-efficient Static Trees and Graphs", "PWL NYC", "PWL NYC", "2020-01-03", "https://paperswelove.org/videos/"),
    ("Serverless Computing: One step forward and two steps backward", "Nyah Check", "PWL SF", "2019-11-21", "https://paperswelove.org/videos/"),
    ("The death of an end-to-end internet (and a way forward)", "Jana Iyengar", "PWL SF", "2019-10-22", "https://paperswelove.org/videos/"),
    ("On the Expressive Power of Programming Languages", "Shriram Krishnamurthi", "PWLConf", "2019-09-19", "https://paperswelove.org/videos/"),
    ("Anonymity in the Bitcoin Peer-to-Peer Network", "Giulia Fanti", "PWLConf", "2019-09-19", "https://paperswelove.org/videos/"),
    ("Distributed Consensus Revised", "Heidi Howard", "PWLConf", "2019-09-19", "https://paperswelove.org/videos/"),
    ("Wait-Free Synchronization", "John Valois", "PWL NYC", "2019-05-14", "https://paperswelove.org/videos/"),
    ("Guaranteeing Consensus in Distributed Systems with CRDTs", "Sun-Li Beatteay", "PWL NYC", "2019-04-18", "https://paperswelove.org/videos/"),
    ("Exception Handling: Issues and a Proposed Notation", "Sarah Groff Palermo", "PWL NYC", "2019-04-17", "https://paperswelove.org/videos/"),
    ("Impossibility of Distributed Consensus with One Faulty Process (FLP)", "John Feminella", "PWL NYC", "2019-03-05", "https://paperswelove.org/videos/"),
    ("Dapper, a Large-Scale Distributed Systems Tracing Infrastructure", "André Freitas", "PWL Porto", "2019-01-30", "https://paperswelove.org/videos/"),
    ("Time, Clocks and Ordering of Events in a Distributed System", "Dan Rubenstein", "PWL NYC", "2019-01-03", "https://paperswelove.org/videos/"),
    ("A Tutorial on Thompson Sampling", "Lydia Gu", "PWL NYC", "2018-12-09", "https://paperswelove.org/videos/"),
    ("Consensus algorithms, Paxos and Raft", "Yifan Xing", "PWL BOS", "2018-11-13", "https://paperswelove.org/videos/"),
    ("A Rehabilitation of Message-passing Concurrency", "Frank Pfenning", "PWLConf", "2018-10-20", "https://paperswelove.org/videos/"),
    ("The Rsync Algorithm", "Camilo Aguilar", "PWL NYC", "2018-10-18", "https://paperswelove.org/videos/"),
    ("Computing Machinery and Intelligence", "Matthew Bergman", "PWL NYC", "2018-10-18", "https://paperswelove.org/videos/"),
    ("The Connection Machine", "Dan Bentley", "PWL NYC", "2018-10-18", "https://paperswelove.org/videos/"),
    ("Bitcoin: A Peer-to-Peer Electronic Cash System", "John Feminella", "PWL NYC", "2018-10-18", "https://paperswelove.org/videos/"),
    ("Peeking Behind the Curtains of Serverless Frameworks", "Gwen Shapira", "PWL SF", "2018-10-07", "https://paperswelove.org/videos/"),
    ("Chord: A Scalable Peer-to-peer Lookup Service", "Aaron Goldman", "PWL SF", "2018-10-07", "https://paperswelove.org/videos/"),
    ("Pastry: Scalable, decentralized object location and routing", "Douglas Creager", "PWL BOS", "2018-07-30", "https://paperswelove.org/videos/"),
    ("Communicating Sequential Processes", "Carmen Andoh", "PWL NYC", "2018-07-28", "https://paperswelove.org/videos/"),
    ("Correcting A Widespread Error in Unification Algorithms", "Sandy Vanderbleek", "PWL", "2018-06-21", "https://paperswelove.org/videos/"),
    ("Ethereum: The World Computer", "Libby Kent", "PWL NYC", "2018-06-12", "https://paperswelove.org/videos/"),
    ("An Efficient Context-Free Parsing Algorithm", "Scott Vokes", "PWL SF", "2018-06-10", "https://paperswelove.org/videos/"),
    ("HyperLogLog: the analysis of a near-optimal cardinality estimation algorithm", "Ben Linsay", "PWL NYC", "2018-06-06", "https://paperswelove.org/videos/"),
    ("Overlapping Experiment Infrastructure", "Scott Andreas", "PWL SF", "2018-06-03", "https://paperswelove.org/videos/"),
    ("What Have We Learned from the PDP-11?", "Dave Cheney", "PWL SF", "2018-06-03", "https://paperswelove.org/videos/"),
    ("Bulletproofs: Short Proofs for Confidential Transactions and More", "Cathie Yun", "PWL SF", "2018-06-01", "https://paperswelove.org/videos/"),
    ("Pivot Tracing: Dynamic Causal Monitoring for Distributed Systems", "Ben Sigelman", "PWL SF", "2018-03-31", "https://paperswelove.org/videos/"),
    ("Designing and Deploying Internet Scale Services", "Kolton Andrus", "PWL SF", "2018-03-31", "https://paperswelove.org/videos/"),
    ("BBR Congestion Control", "Hannes Sowa", "PWL NYC", "2018-03-28", "https://paperswelove.org/videos/"),
    ("Out of the Tar Pit", "Diogo Biazus", "PWL TO", "2017-12-19", "https://paperswelove.org/videos/"),
    ("Getting from A to B: fast route finding on slow computers", "Simon Peyton Jones", "PWL London", "2017-11-21", "https://paperswelove.org/videos/"),
    ("SCONE: Secure Linux Containers with Intel SGX", "Jessie Frazelle", "PWL NYC", "2017-11-06", "https://paperswelove.org/videos/"),
    ("ARC: A Self-Tuning, Low Overhead Replacement Cache", "Bryan Cantrill", "PWL SF", "2017-10-17", "https://paperswelove.org/videos/"),
    ("Out of the Tar Pit", "Diogo Biazus", "PWL TO", "2017-12-19", "https://paperswelove.org/videos/"),
    ("Off-the-Record Communication, or, Why Not To Use PGP", "Wes Chow", "PWL NYC", "2017-09-15", "https://paperswelove.org/videos/"),
    ("Realtime Data Processing at Facebook", "Gwen Shapira", "PWL QCon NYC", "2017-08-02", "https://paperswelove.org/videos/"),
    ("Scuba: Diving into Data at Facebook", "Charity Majors", "PWL QCon NYC", "2017-08-02", "https://paperswelove.org/videos/"),
    ("Curve25519 and Fast Public Key Cryptography", "Kevin Burke", "PWL SF", "2017-07-31", "https://paperswelove.org/videos/"),
    ("DeepStack: Expert-Level Artificial Intelligence in No-Limit Poker", "Tom Santero", "PWL SF", "2017-07-06", "https://paperswelove.org/videos/"),
    ("A Mathematical Theory of Communication", "Kiran Bhattaram", "PWL SF", "2017-07-06", "https://paperswelove.org/videos/"),
    ("The Most Beautiful Program Ever Written", "William Byrd", "PWL NYC", "2017-05-24", "https://paperswelove.org/videos/"),
    ("Failure Detectors", "Kiran Bhattaram", "PWL", "2017-04-13", "https://paperswelove.org/videos/"),
    ("No Silver Bullet — Essence and Accidents of Software Engineering", "Dr. Fred Brooks", "PWL Raleigh-Durham", "2017-04-12", "https://paperswelove.org/videos/"),
    ("Distributed Programming in Argus", "Caitie McCaffrey", "PWL", "2017-03-16", "https://paperswelove.org/videos/"),
    ("Causes and Explanations: A Structural-Model Approach", "Peter Alvaro", "PWL", "2017-03-16", "https://paperswelove.org/videos/"),
    ("The criteria to be used in decomposing systems into modules", "Diego Ongaro", "PWL SF", "2017-03-15", "https://paperswelove.org/videos/"),
    ("A Brief History of NTP Time", "Bryan Fink", "PWL SF", "2017-03-15", "https://paperswelove.org/videos/"),
    ("Definitional Interpreters for Higher-Order Programming Languages", "Philip Wadler", "PWL Remote", "2017-01-24", "https://paperswelove.org/videos/"),
    ("The Rendering Equation", "Wil Yegelwel", "PWL", "2017-01-23", "https://paperswelove.org/videos/"),
    ("The Weakest Failure Detector for Solving Consensus", "David Kua", "PWL TO", "2016-12-08", "https://paperswelove.org/videos/"),
    ("A New Approach to Linear Filtering and Prediction Problems (Kalman Filter)", "Elizabeth Ramirez", "PWL", "2016-11-10", "https://paperswelove.org/videos/"),
    ("A Protocol for Interledger Payments", "Tony Arcieri", "PWL", "2016-10-20", "https://paperswelove.org/videos/"),
    ("The Design and Implementation of a Log-Structured File System", "Ding Yuan", "PWL TO", "2016-10-07", "https://paperswelove.org/videos/"),
    ("Vivaldi: A Decentralized Network Coordinate System", "Armon Dadgar", "PWL", "2016-09-27", "https://paperswelove.org/videos/"),
    ("Randomized Gossip Methods", "Dahlia Malkhi", "PWLConf", "2016-09-26", "https://paperswelove.org/videos/"),
    ("Reflection without Remorse", "Suhail Shergill", "PWL TO", "2016-09-14", "https://paperswelove.org/videos/"),
    ("CRDTs: Commutative Replicated Data Types", "Paul Osman", "PWL TO", "2016-09-14", "https://paperswelove.org/videos/"),
    ("Tracing the Meta-Level: PyPy's Tracing JIT Compiler", "Scott Rostrup", "PWL TO", "2016-09-14", "https://paperswelove.org/videos/"),
    ("Chain Replication", "Deniz Altınbüken", "PWL", "2016-08-20", "https://paperswelove.org/videos/"),
    ("Tiered Replication: A Cost-effective Alternative to Full Cluster Geo-replication", "Wes Chow", "PWL", "2016-08-20", "https://paperswelove.org/videos/"),
    ("Propositions as Types", "Paul Snively", "PWL", "2016-06-07", "https://paperswelove.org/videos/"),
    ("Sagas", "Caitie McCaffrey", "PWL SF", "2016-03-18", "https://paperswelove.org/videos/"),
    ("A Scalable Bootstrap for Massive Data", "Matt Adereth", "PWL SF", "2016-03-05", "https://paperswelove.org/videos/"),
    ("Jails and Solaris Zones", "Bryan Cantrill", "PWL", "2016-03-03", "https://paperswelove.org/videos/"),
    ("No compromises: distributed transactions with consistency, availability, and performance", "Henry Robinson", "PWL SF", "2016-01-22", "https://paperswelove.org/videos/"),
    ("Logical Time", "Jordan West", "PWL SF", "2016-01-22", "https://paperswelove.org/videos/"),
    ("Probabilistic Accuracy Bounds for Fault-Tolerant Computations", "Aysylu Greenberg", "PWL SF", "2015-12-14", "https://paperswelove.org/videos/"),
    ("Epidemic Algorithms for Replicated Database Maintenance", "Jason Brown", "PWL SF", "2015-12-13", "https://paperswelove.org/videos/"),
    ("Macaroons: Cookies with Contextual Caveats", "Sam L'ecuyer", "PWL", "2015-11-03", "https://paperswelove.org/videos/"),
    ("An Industrial-Strength Audio Search Algorithm", "Peter Sobot", "PWL TO", "2015-10-16", "https://paperswelove.org/videos/"),
    ("Programming with Algebraic Effects and Handlers", "Ben Darwin", "PWL TO", "2015-10-16", "https://paperswelove.org/videos/"),
    ("Memory by the Slab: The Tale of Bonwick's Slab Allocator", "Ryan Zezeski", "PWL", "2015-10-13", "https://paperswelove.org/videos/"),
    ("µKanren: A Minimal Functional Core for Relational Programming", "Bodil Stokke", "PWL", "2015-10-13", "https://paperswelove.org/videos/"),
    ("Hints for Computer System Design", "Bill Berry", "PWL", "2015-08-20", "https://paperswelove.org/videos/"),
    ("Making a Fast Curry: Push/Enter vs. Eval/Apply for Higher-order Languages", "Jason Ganetsky", "PWL", "2015-08-12", "https://paperswelove.org/videos/"),
    ("Nonblocking Algorithms & Scalable Multicore Programming", "Devon O'Dell", "PWL SF", "2015-07-02", "https://paperswelove.org/videos/"),
    ("Principal type-schemes for functional programs (Hindley-Milner)", "Phil Freeman", "PWL", "2015-06-25", "https://paperswelove.org/videos/"),
    ("Raft: In Search of an Understandable Consensus Algorithm", "Donny Nadolny", "PWL TO", "2015-06-25", "https://paperswelove.org/videos/"),
    ("Making Lockless Synchronization Fast", "Samy Al Bahra", "PWL", "2015-06-24", "https://paperswelove.org/videos/"),
    ("Architectural Styles and the Design of Network-based Software (REST)", "Mark Masse", "PWL", "2015-06-04", "https://paperswelove.org/videos/"),
    ("An Axiomatic Basis for Computer Programming (Hoare Logic)", "Ryan Nichols/Jean Yang", "PWL", "2015-05-08", "https://paperswelove.org/videos/"),
    ("The Scalable Commutativity Rule", "Neha Narula", "PWL", "2015-04-06", "https://paperswelove.org/videos/"),
    ("Bloom Filters and HyperLogLog", "Armon Dadgar", "PWL SF", "2015-03-31", "https://paperswelove.org/videos/"),
    ("Fundamental Concepts in Programming Languages", "John Myles White", "PWL", "2015-03-24", "https://paperswelove.org/videos/"),
    ("Orleans: A Framework for Cloud Computing", "Caitie McCaffrey", "PWL SF", "2015-03-06", "https://paperswelove.org/videos/"),
    ("Incremental Mature Garbage Collection Using the Train Algorithm", "Andrew Turley", "PWL", "2015-03-02", "https://paperswelove.org/videos/"),
    ("Composable and Compilable Macros", "Sam Tobin-Hochstadt", "PWL", "2015-02-12", "https://paperswelove.org/videos/"),
    ("Managing Update Conflicts in Bayou", "Peter Bailis", "PWL SF", "2015-01-26", "https://paperswelove.org/videos/"),
    ("The Chubby lock service for loosely-coupled distributed systems", "Camille Fournier", "PWL", "2014-12-26", "https://paperswelove.org/videos/"),
    ("On the resemblance and containment of documents", "Jeff Larson", "PWL", "2014-12-26", "https://paperswelove.org/videos/"),
    ("Level Ancestor Simplified", "Leif Walsh", "PWL SF", "2014-11-18", "https://paperswelove.org/videos/"),
    ("Chord: A Scalable P2P Lookup Service for Internet Applications", "John-Alan Simmons", "PWL TO", "2014-11-09", "https://paperswelove.org/videos/"),
    ("The Derivative of a Regular Type is its Type of One-Hole Contexts", "Erik Hinton", "PWL", "2014-09-14", "https://paperswelove.org/videos/"),
    ("One VM to Rule Them All", "Aysylu Greenberg", "PWL", "2014-09-14", "https://paperswelove.org/videos/"),
    ("SWIM: Scalable Weakly-consistent Infection-style Process Group Membership", "Armon Dadgar", "PWL SF", "2014-10-07", "https://paperswelove.org/videos/"),
    ("Using Reasoning about Knowledge to Analyze Distributed Systems", "Peter Alvaro", "PWL SF", "2014-10-07", "https://paperswelove.org/videos/"),
    ("Sparrow: Distributed, Low Latency Scheduling", "David Greenberg", "PWL", "2014-06-18", "https://paperswelove.org/videos/"),
    ("Calvin: Fast Distributed Transactions for Partitioned Database Systems", "Joel VanderWerf", "PWL SF", "2014-06-06", "https://paperswelove.org/videos/"),
    ("Bimodal Multicast", "Bruce Spang", "PWL SF", "2014-05-23", "https://paperswelove.org/videos/"),
    ("Dapper, a Large-Scale Distributed Systems Tracing Infrastructure", "Ryan Kennedy, Anjali Shenoy", "PWL SF", "2014-05-07", "https://paperswelove.org/videos/"),
    ("The Akamai Network", "Andy Gross", "PWL SF", "2014-05-07", "https://paperswelove.org/videos/"),
    ("A Unified Theory of Garbage Collection", "Michael Bernstein", "PWL", "2014-02-28", "https://paperswelove.org/videos/"),
]

# ============================================================
# SOURCE 4: Arpit Bhayani's Papershelf
# ============================================================

ARPIT_PAPERS = [
    ("On-demand Container Loading in AWS Lambda", "Arpit Bhayani", "https://arpitbhayani.me/blogs/on-demand-container-loading-in-aws-lambda"),
    ("SQL Has Problems. We Can Fix Them: Pipe Syntax In SQL", "Arpit Bhayani", "https://arpitbhayani.me/blogs/sql-has-problems-we-can-fix-them-pipe-syntax-in-sql"),
    ("NanoLog: A Nanosecond Scale Logging System", "Arpit Bhayani", "https://arpitbhayani.me/blogs/nanolog-a-nanosecond-scale-logging-system"),
    ("WTF: The Who to Follow Service at Twitter", "Arpit Bhayani", "https://arpitbhayani.me/blogs/wtf-the-who-to-follow-service-at-twitter"),
]

# ============================================================
# HIGH-LEVEL SECTION MAPPING (same as before)
# ============================================================

SECTIONS = {
    "Distributed Systems & Consensus": [
        "Distributed Systems", "Consistency", "Concurrency",
        "Blockchain", "Transaction processing"
    ],
    "Machine Learning & AI": [
        "Machine Learning", "Deep Learning", "AI",
        "Data Science", "Analytics"
    ],
    "Database Systems & Data Engines": [
        "Datastores", "Storage", "Stream processing",
        "Time series", "Graph", "Web Scale"
    ],
    "Software Engineering, Testing, & Security": [
        "Software Engineering", "Testing", "Security",
        "Privacy", "Formal methods", "Ethics", "Operations"
    ],
    "Operating Systems, Networks, & Hardware": [
        "Operating Systems", "Networking", "Hardware",
        "Containers", "Virtualization", "IoT", "mobile", "Scheduling"
    ],
    "Programming Languages & Algorithms": [
        "Programming Languages", "Programming",
        "Algorithms and data structures"
    ],
    "By Company": [
        "Amazon", "Facebook", "Google", "Microsoft"
    ],
    "More Topics": [
        "Great moments", "HCI", "Provenance", "quantum",
        "Robotics", "Social Networks"
    ],
}

# New sections for non-Acolyer sources
EXTRA_SECTIONS = {
    "📚 Marc Brooker's Essential Reading": {
        "Essential Leslie Lamport": BROOKER_LAMPORT,
        "Essential Nancy Lynch": BROOKER_LYNCH,
        "Essential Barbara Liskov": BROOKER_LISKOV,
    },
    "🎥 Papers We Love Videos": {
        "All Videos": PWL_VIDEOS,
    },
    "📝 Arpit Bhayani's Paper Notes": {
        "Paper Notes": ARPIT_PAPERS,
    },
}


def esc(text):
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def build_acolyer_section(section_name, tag_names, categories):
    """Build HTML for an Acolyer section."""
    total = 0
    tags_html = ""
    for tag_name in tag_names:
        if tag_name not in categories:
            continue
        posts = categories[tag_name]
        if not posts:
            continue
        total += len(posts)
        post_items = ""
        for p in posts:
            title = esc(p["title"])
            url = esc(p["url"])
            date = p.get("date", "")
            post_items += f'                    <li><a href="{url}" class="block py-1 hover:text-[#C8102E] transition-colors motion-safe:transition-colors"><span class="text-stone-900/70 dark:text-stone-50/70 text-xs tabular-nums mr-2">{date}</span>{title}</a></li>\n'
        tag_id = tag_name.lower().replace(" ", "-").replace(",", "")
        tags_html += f"""
                <div class="border border-stone-200 dark:border-stone-800 rounded-sm">
                    <button onclick="toggleCategory('{tag_id}')"
                            class="w-full flex items-center justify-between px-4 py-3 text-left hover:bg-stone-100 dark:hover:bg-stone-800 transition-colors motion-safe:transition-colors focus-visible:ring-2 focus-visible:ring-[#C8102E] focus-visible:outline-none min-h-[44px]"
                            aria-expanded="false" aria-controls="cat-{tag_id}">
                        <span class="text-base font-medium text-stone-900 dark:text-stone-50">{tag_name}</span>
                        <span class="flex items-center gap-2">
                            <span class="text-xs text-stone-900/40 dark:text-stone-50/40 tabular-nums">{len(posts)}</span>
                            <svg class="w-4 h-4 text-stone-900/40 dark:text-stone-50/40 transition-transform motion-safe:transition-transform" id="icon-{tag_id}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
                            </svg>
                        </span>
                    </button>
                    <div id="cat-{tag_id}" class="hidden">
                        <ul class="px-4 pb-3 space-y-0.5 max-h-[60vh] overflow-y-auto">{post_items}                        </ul>
                    </div>
                </div>"""
    section_id = section_name.lower().replace(" ", "-").replace(",", "").replace("&", "and")
    return f"""
            <section class="py-16 md:py-20 border-b border-stone-200 dark:border-stone-800" id="{section_id}">
                <div class="max-w-5xl mx-auto px-4 md:px-8">
                    <div class="flex items-baseline justify-between mb-8">
                        <h2 class="text-2xl md:text-3xl font-light tracking-tight text-stone-900 dark:text-stone-50 text-balance">{section_name}</h2>
                        <span class="text-xs text-stone-900/40 dark:text-stone-50/40 tabular-nums">{total} papers</span>
                    </div>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">{tags_html}                    </div>
                </div>
            </section>"""


def build_extra_section(section_name, subsections):
    """Build HTML for non-Acolyer sections (Brooker, PWL, Arpit)."""
    total = 0
    tags_html = ""
    for sub_name, papers in subsections.items():
        total += len(papers)
        tag_id = sub_name.lower().replace(" ", "-").replace(",", "").replace(":", "").replace(".", "")
        post_items = ""
        for p in papers:
            if len(p) == 5:
                third = p[2]
                if third and third[:4].isdigit():
                    # Brooker: (title, authors, year, description, url)
                    title, authors, year, desc, url = p
                    title_link = f'<a href="{url}" target="_blank" rel="noopener" class="hover:text-[#C8102E] underline decoration-stone-300/50 hover:decoration-[#C8102E]/40 underline-offset-2 transition-colors motion-safe:transition-colors">{esc(title)}</a>'
                    post_items += f'                    <li class="py-2"><div class="text-stone-900 dark:text-stone-50">{title_link}</div><div class="text-xs text-stone-900/50 dark:text-stone-50/50 mt-0.5">{esc(authors)} · {year} — {esc(desc)}</div></li>\n'
                else:
                    # PWL: (title, presenter, chapter, date, url)
                    title, presenter, chapter, date, url = p
                    post_items += f'                    <li><a href="{url}" class="block py-1 hover:text-[#C8102E] transition-colors motion-safe:transition-colors"><span class="text-stone-900/70 dark:text-stone-50/70 text-xs tabular-nums mr-2">{date}</span>{esc(title)}</a><span class="text-xs text-stone-900/40 dark:text-stone-50/40 ml-2">{esc(presenter)} · {esc(chapter)}</span></li>\n'
            elif len(p) == 3:  # Arpit: (title, author, url)
                title, author, url = p
                post_items += f'                    <li><a href="{url}" class="block py-1 hover:text-[#C8102E] transition-colors motion-safe:transition-colors">{esc(title)}</a><span class="text-xs text-stone-900/40 dark:text-stone-50/40 ml-2">— {esc(author)}</span></li>\n'
        tags_html += f"""
                <div class="border border-stone-200 dark:border-stone-800 rounded-sm">
                    <button onclick="toggleCategory('{tag_id}')"
                            class="w-full flex items-center justify-between px-4 py-3 text-left hover:bg-stone-100 dark:hover:bg-stone-800 transition-colors motion-safe:transition-colors focus-visible:ring-2 focus-visible:ring-[#C8102E] focus-visible:outline-none min-h-[44px]"
                            aria-expanded="false" aria-controls="cat-{tag_id}">
                        <span class="text-base font-medium text-stone-900 dark:text-stone-50">{sub_name}</span>
                        <span class="flex items-center gap-2">
                            <span class="text-xs text-stone-900/40 dark:text-stone-50/40 tabular-nums">{len(papers)}</span>
                            <svg class="w-4 h-4 text-stone-900/40 dark:text-stone-50/40 transition-transform motion-safe:transition-transform" id="icon-{tag_id}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
                            </svg>
                        </span>
                    </button>
                    <div id="cat-{tag_id}" class="hidden">
                        <ul class="px-4 pb-3 space-y-0.5 max-h-[60vh] overflow-y-auto">{post_items}                        </ul>
                    </div>
                </div>"""
    section_id = section_name.lower().replace(" ", "-").replace(",", "").replace("&", "and").replace("📚", "").replace("🎥", "").replace("📝", "").replace(":", "").strip()
    return f"""
            <section class="py-16 md:py-20 border-b border-stone-200 dark:border-stone-800" id="{section_id}">
                <div class="max-w-5xl mx-auto px-4 md:px-8">
                    <div class="flex items-baseline justify-between mb-8">
                        <h2 class="text-2xl md:text-3xl font-light tracking-tight text-stone-900 dark:text-stone-50 text-balance">{section_name}</h2>
                        <span class="text-xs text-stone-900/40 dark:text-stone-50/40 tabular-nums">{total} entries</span>
                    </div>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">{tags_html}                    </div>
                </div>
            </section>"""


def build_html():
    categories = acolyer["categories"]
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # Build Acolyer sections
    acolyer_html = ""
    for section_name, tag_names in SECTIONS.items():
        acolyer_html += build_acolyer_section(section_name, tag_names, categories)

    # Build extra sections
    extra_html = ""
    for section_name, subsections in EXTRA_SECTIONS.items():
        extra_html += build_extra_section(section_name, subsections)

    # Stats
    total_acolyer = sum(len(v) for v in categories.values())
    unique_acolyer = len(set(p["url"] for v in categories.values() for p in v))
    total_brooker = sum(len(v) for v in EXTRA_SECTIONS["📚 Marc Brooker's Essential Reading"].values())
    total_pwl = sum(len(v) for v in EXTRA_SECTIONS["🎥 Papers We Love Videos"].values())
    total_arpit = sum(len(v) for v in EXTRA_SECTIONS["📝 Arpit Bhayani's Paper Notes"].values())

    all_section_keys = list(SECTIONS.keys()) + list(EXTRA_SECTIONS.keys())

    html = f"""<!DOCTYPE html>
<html lang="en" class="scroll-smooth">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="color-scheme" content="light dark">
    <meta name="theme-color" content="#fafaf9" media="(prefers-color-scheme: light)">
    <meta name="theme-color" content="#0c0a09" media="(prefers-color-scheme: dark)">
    <title>Papershelf · Paper Index</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:ital,wght@0,300;0,400;0,500;0,600;1,300;1,400&display=swap" rel="stylesheet">
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {{
            darkMode: 'media',
            theme: {{
                fontFamily: {{
                    sans: ['IBM Plex Sans', 'Hanken Grotesk', 'Barlow', 'Host Grotesk', 'DM Sans', 'system-ui', 'sans-serif'],
                }}
            }}
        }}
    </script>
    <style>
        html {{ color-scheme: light dark; }}
        body {{ font-family: 'IBM Plex Sans', 'Hanken Grotesk', 'Barlow', 'Host Grotesk', 'DM Sans', system-ui, sans-serif; }}
    </style>
</head>
<body class="bg-stone-50 dark:bg-stone-950 text-stone-900 dark:text-stone-50 antialiased">

    <!-- Header -->
    <header class="border-b border-stone-200 dark:border-stone-800 sticky top-0 bg-stone-50/95 dark:bg-stone-950/95 backdrop-blur-sm z-10">
        <div class="max-w-5xl mx-auto px-4 md:px-8 py-6">
            <div class="flex flex-col sm:flex-row sm:items-baseline sm:justify-between gap-4">
                <div>
                    <h1 class="text-3xl md:text-4xl font-light tracking-tight text-stone-900 dark:text-stone-50 text-balance">Papershelf</h1>
                    <p class="text-sm text-stone-900/50 dark:text-stone-50/50 mt-1">A curated index of Computer Science paper breakdowns from across the web</p>
                </div>
                <div class="flex items-center gap-4">
                    <span class="text-xs text-stone-900/40 dark:text-stone-50/40 tabular-nums">{total_acolyer + total_brooker + total_pwl + total_arpit} entries · {unique_acolyer} Acolyer papers + {total_brooker} Brooker refs + {total_pwl} PWL videos + {total_arpit} Arpit notes</span>
                </div>
            </div>
            <!-- Search -->
            <div class="mt-4 relative">
                <input type="text" id="search" placeholder="Search all papers…"
                       class="w-full px-4 py-2 bg-stone-100 dark:bg-stone-900 border border-stone-200 dark:border-stone-800 rounded-sm text-base text-stone-900 dark:text-stone-50 placeholder:text-stone-900/30 dark:placeholder:text-stone-50/30 focus:outline-none focus-visible:ring-2 focus-visible:ring-[#C8102E] transition-colors motion-safe:transition-colors"
                       oninput="filterPapers()">
                <span id="search-count" class="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-stone-900/30 dark:text-stone-50/30 hidden"></span>
            </div>
            <!-- Quick nav -->
            <nav class="mt-4 flex flex-wrap gap-2" aria-label="Jump to section">
                {''.join(f'<a href="#{s.lower().replace(" ", "-").replace(",", "").replace("&", "and").replace("📚", "").replace("🎥", "").replace("📝", "").replace(":", "").strip()}" class="text-xs px-2 py-1 bg-stone-100 dark:bg-stone-800 border border-stone-200 dark:border-stone-700 rounded-sm hover:border-[#C8102E]/40 hover:text-[#C8102E] transition-colors motion-safe:transition-colors focus-visible:ring-2 focus-visible:ring-[#C8102E] focus-visible:outline-none min-h-[44px] min-w-[44px] inline-flex items-center">{s}</a>' for s in all_section_keys)}
            </nav>
            <!-- Sources -->
            <div class="mt-3 flex flex-wrap gap-3 text-xs text-stone-900/40 dark:text-stone-50/40">
                <span>Sources: <a href="https://blog.acolyer.org" class="underline hover:text-[#C8102E]">The Morning Paper</a> · <a href="https://brooker.co.za/blog/" class="underline hover:text-[#C8102E]">Marc Brooker</a> · <a href="https://paperswelove.org/videos/" class="underline hover:text-[#C8102E]">Papers We Love</a> · <a href="https://arpitbhayani.me/papershelf/" class="underline hover:text-[#C8102E]">Arpit Bhayani</a></span>
            </div>
        </div>
    </header>

    <main>
        <!-- Acolyer sections -->
{acolyer_html}
        <!-- Extra sections -->
{extra_html}
    </main>

    <!-- Footer -->
    <footer class="py-16 border-t border-stone-200 dark:border-stone-800">
        <div class="max-w-5xl mx-auto px-4 md:px-8 text-center">
            <p class="text-xs text-stone-900/40 dark:text-stone-50/40">
                Papershelf · Generated {now}<br>
                Acolyer papers © Adrian Colyer · Brooker lists © Marc Brooker · PWL videos © Papers We Love · Arpit notes © Arpit Bhayani<br>
                Built as a community index for personal research use
            </p>
        </div>
    </footer>

    <script>
        function toggleCategory(id) {{
            const panel = document.getElementById('cat-' + id);
            const icon = document.getElementById('icon-' + id);
            const button = panel.previousElementSibling;
            const isOpen = !panel.classList.contains('hidden');
            if (isOpen) {{
                panel.classList.add('hidden');
                icon.style.transform = 'rotate(0deg)';
                button.setAttribute('aria-expanded', 'false');
            }} else {{
                panel.classList.remove('hidden');
                icon.style.transform = 'rotate(180deg)';
                button.setAttribute('aria-expanded', 'true');
            }}
        }}

        function filterPapers() {{
            const query = document.getElementById('search').value.toLowerCase().trim();
            const countEl = document.getElementById('search-count');
            const sections = document.querySelectorAll('main > section');
            let visibleSections = 0;

            sections.forEach(section => {{
                const buttons = section.querySelectorAll('button[onclick^="toggleCategory"]');
                let sectionHasVisible = false;

                buttons.forEach(button => {{
                    const panelId = button.getAttribute('aria-controls');
                    const panel = document.getElementById(panelId);
                    const container = button.parentElement;
                    const items = panel.querySelectorAll('li');
                    let anyVisible = false;

                    items.forEach(item => {{
                        const text = item.textContent.toLowerCase();
                        if (!query || text.includes(query)) {{
                            item.style.display = '';
                            anyVisible = true;
                        }} else {{
                            item.style.display = 'none';
                        }}
                    }});

                    if (anyVisible || !query) {{
                        container.style.display = '';
                        sectionHasVisible = true;
                        if (query && anyVisible) {{
                            panel.classList.remove('hidden');
                            const icon = container.querySelector('svg');
                            if (icon) icon.style.transform = 'rotate(180deg)';
                            button.setAttribute('aria-expanded', 'true');
                        }}
                    }} else {{
                        container.style.display = 'none';
                    }}
                }});

                if (sectionHasVisible || !query) {{
                    section.style.display = '';
                    visibleSections++;
                }} else {{
                    section.style.display = 'none';
                }}
            }});

            if (query) {{
                countEl.classList.remove('hidden');
                countEl.textContent = visibleSections + ' sections';
            }} else {{
                countEl.classList.add('hidden');
                document.querySelectorAll('[id^="cat-"]').forEach(p => p.classList.add('hidden'));
                document.querySelectorAll('button[onclick^="toggleCategory"]').forEach(b => b.setAttribute('aria-expanded', 'false'));
                document.querySelectorAll('svg[id^="icon-"]').forEach(s => s.style.transform = 'rotate(0deg)');
            }}
        }}
    </script>
</body>
</html>
"""
    return html


def main():
    html = build_html()
    with open(OUTPUT_FILE, "w") as f:
        f.write(html)
    print(f"Generated {OUTPUT_FILE}")
    
    # Stats
    total = sum(len(v) for v in acolyer["categories"].values())
    unique = len(set(p["url"] for v in acolyer["categories"].values() for p in v))
    print(f"Acolyer: {total} entries, {unique} unique papers, {len(acolyer['categories'])} categories")
    print(f"Brooker Liskov: {len(BROOKER_LISKOV)} papers")
    print(f"Brooker Lamport: {len(BROOKER_LAMPORT)} papers")
    print(f"Brooker Lynch: {len(BROOKER_LYNCH)} papers")
    print(f"PWL Videos: {len(PWL_VIDEOS)} videos")
    print(f"Arpit Papers: {len(ARPIT_PAPERS)} paper notes")


if __name__ == "__main__":
    main()
