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
# DISTRIBUTED SYSTEMS SUB-CATEGORIZATION
# ============================================================

DS_SUB_RULES = [
    ("Consensus, Replication & Consistency",
     ["consensus", "paxos", "raft", "bft", "viewstamped", "atomic broadcast", "zab", "quorum", "consistency", "replicat", "Linearizability", "Serializability", "fault", "leased", "leader", "calm"],
     ["Consistency", "Transaction processing", "Blockchain"]),
    ("Shared Logs, Coordination & Locks",
     ["shared log", "corfu", "fuzzylog", "coordination", "lock", "chubby", "zookeeper", "drinking philosopher", "blaze", "common knowledge", "heard-of", "extensible distributed", "life beyond distributed"],
     ["Concurrency"]),
    ("Observability, Tracing & Debugging",
     ["tracing", "debugg", "partial failure", "pivot", "dapper", "kraken", "monitoring", "log recon", "profiler", "lprof", "bigdebug", "random test", "canopy", "mystery machine", "app-bisect", "seer"],
     ["Operations", "Testing"]),
    ("Distributed Storage, Databases & Memory",
     ["aurora", "calvin", "anna", "ramcloud", "vcorfu", "tachyon", "ipfs", "faw", "memory disagg", "infiniswap", "hopfs", "checkpoint"],
     ["Datastores", "Storage"]),
    ("Networking & Communication",
     ["rpc", "maglev", "kv-direct", "network", "load balanc", "brownout", "cross-layer"],
     ["Networking"]),
    ("Scheduling & Resource Management",
     ["borg", "yarn", "schedul", "provision", "morpheus", "heracles", "hcloud", "blade", "panopticon", "tail at scale", "smoothoperator", "slicer"],
     ["Scheduling"]),
    ("Formal Methods, Verification & Theory",
     ["formal", "verif", "model check", "ironfleet", "proof", "virtual time", "snapshot", "termination", "tla", "samc"],
     ["Formal methods"]),
    ("Performance, Benchmarking & Resilience",
     ["benchmark", "performance", "wsmete", "cherrypick", "skyway", "fit", "overload", "resilien", "cloudburst", "serverless", "occupy"],
     ["Performance"]),
    ("Infrastructure at Scale",
     ["warehouse", "datacenter", "microservice", "servicefabric", "gray failure", "brownout"],
     ["Google", "Facebook", "Amazon", "Microsoft", "Containers"]),
    ("Distributed ML, Dataflows & Edge",
     ["tensorflow", "machine learning", "deep learn", "deep neural", "petuum", "geeps", "dataflow", "derflow", "edge", "offload", "sttr", "scootr", "spark", "actor"],
     ["Machine Learning", "Deep Learning", "Data Science"]),
    ("Software Design & Programming Models",
     ["local-first", "end-to-end", "reading list", "fire swamp", "design", "programming model", "internet-scale", "scalability! but", "data on the outside", "cost?"],
     ["Software Engineering", "Programming Languages"]),
    ("CRDTs & Convergent Types",
     ["crdt", "replicated data type", "mergeable", "convergent", "delta state", "commutative"],
     []),
]

def split_ds_papers(categories):
    """Split Distributed Systems papers into thematic sub-categories."""
    ds_papers = categories.get("Distributed Systems", [])
    if not ds_papers:
        return {}
    
    # Build a URL -> set of tags map for quick lookup
    url_tags = {}
    for tag_name, tag_papers in categories.items():
        for p in tag_papers:
            url_tags.setdefault(p["url"], set()).add(tag_name)
    
    buckets = {name: [] for name, _, _ in DS_SUB_RULES}
    buckets["Other Distributed Systems"] = []
    
    for p in ds_papers:
        title_lower = p["title"].lower()
        ptags = url_tags.get(p["url"], set())
        assigned = False
        for sub_name, keywords, co_tags in DS_SUB_RULES:
            if any(kw in title_lower for kw in keywords):
                buckets[sub_name].append(p)
                assigned = True
                break
            if any(ct in ptags for ct in co_tags):
                buckets[sub_name].append(p)
                assigned = True
                break
        if not assigned:
            buckets["Other Distributed Systems"].append(p)
    
    # Remove empty buckets
    return {k: v for k, v in buckets.items() if v}


# ============================================================
# HIGH-LEVEL SECTION MAPPING
# ============================================================

SECTIONS = {
    "Distributed Systems": [
        "DS::Consensus, Replication & Consistency",
        "DS::Shared Logs, Coordination & Locks",
        "DS::Observability, Tracing & Debugging",
        "DS::Distributed Storage, Databases & Memory",
        "DS::Networking & Communication",
        "DS::Scheduling & Resource Management",
        "DS::Formal Methods, Verification & Theory",
        "DS::Performance, Benchmarking & Resilience",
        "DS::Infrastructure at Scale",
        "DS::Distributed ML, Dataflows & Edge",
        "DS::Software Design & Programming Models",
        "DS::CRDTs & Convergent Types",
        "DS::Other Distributed Systems",
    ],
    "Machine Learning & AI": [
        "Machine Learning", "Deep Learning", "AI",
        "Data Science", "Analytics"
    ],
    "Database Systems & Data Engines": [
        "Datastores", "Storage", "Stream processing",
        "Time series", "Graph", "Web Scale",
        "Transaction processing"
    ],
    "Software Engineering, Testing, & Security": [
        "Software Engineering", "Testing", "Security",
        "Privacy", "Formal methods", "Ethics", "Operations"
    ],
    "Operating Systems, Networks, & Hardware": [
        "Operating Systems", "Networking", "Hardware",
        "Containers", "Virtualization", "IoT", "mobile",
        "Scheduling", "Concurrency"
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
        "Robotics", "Social Networks", "Blockchain",
        "Consistency"
    ],
}

# ============================================================
# SOURCE 4: Arpit Bhayani's Papershelf
# ============================================================

ARPIT_BREAKDOWNS = [
    ("Real-time Data Infrastructure at Uber", "Arpit Bhayani", "https://drive.google.com/file/d/120zrm63AxpWXNHCoY9aOo45mem_zrOcl/view?usp=sharing"),
    ("DeepSeekMath-V2: Towards Self-Verifiable Mathematical Reasoning", "Arpit Bhayani", "https://drive.google.com/file/d/1GRWC0m7_Txzpttwh689Ki4QvPfw7Fzb6/view?usp=sharing"),
    ("Lost in the Middle: How Language Models Use Long Contexts", "Arpit Bhayani", "https://drive.google.com/file/d/16Mp2CjM_AdmItMhFTZjqr47j0U9Fmj13/view?usp=sharing"),
    ("Yedalog: Exploring Knowledge at Scale", "Arpit Bhayani", "https://drive.google.com/file/d/1lSGc9EwLL0YyO54C-P5g45V_ub0PLrfS/view?usp=sharing"),
    ("C/C++ Thread Safety Analysis", "Arpit Bhayani", "https://drive.google.com/file/d/1MefMB5wxgJ8MeDYmzzDyitc8CXtbJUlu/view?usp=sharing"),
    ("Mesa: Geo-Replicated, Near Real-Time, Scalable Data Warehousing", "Arpit Bhayani", "https://drive.google.com/file/d/1A9er-QaeGlQXkVOmvSCXarB2DfFoxQFr/view?usp=sharing"),
    ("MyRocks: LSM-Tree Database Storage Engine Serving Facebook's Social Graph", "Arpit Bhayani", "https://drive.google.com/file/d/1HrL7uhEkWwmi5u8rfPRBXYRFJnn-VOwg/view?usp=sharing"),
    ("Storing and Querying Tree-Structured Records in Dremel", "Arpit Bhayani", "https://drive.google.com/file/d/1ttlkHG_3Vr7jnKnlk7igqSJZV9-SQkbx/view?usp=sharing"),
    ("In praise of empathic AI", "Arpit Bhayani", "https://drive.google.com/file/d/1yBXVlZXdojDCuwW64K_k-5i1-Z1m46Xh/view?usp=drive_link"),
    ("In-Memory Performance for Big Data", "Arpit Bhayani", "https://drive.google.com/file/d/1tk2_z6fwI0swOHidOMp_U17HlO8zU8bT/view?usp=sharing"),
    ("AGILE: elastic distributed resource scaling for Infrastructure-as-a-Service", "Arpit Bhayani", "https://drive.google.com/file/d/1TuOu7ojdn0FRa1RB9qlSj6h0wK8og6Nd/view?usp=sharing"),
    ("Web-scale Job Scheduling", "Arpit Bhayani", "https://drive.google.com/file/d/1F_8IehQpC9yDEM7oeqM5vJi347K3b65w/view?usp=sharing"),
    ("Spanner: Google’s Globally-Distributed Database", "Arpit Bhayani", "https://drive.google.com/file/d/1DWzgQsX0aXkkYNR3Df2zWOe3PBPIzID-/view?usp=sharing"),
    ("Optimizing Google’s Warehouse Scale Computers: The NUMA Experience", "Arpit Bhayani", "https://drive.google.com/file/d/1X_3btCINzqD9kyZsYmcfRYihnPHNxHFh/view?usp=sharing"),
    ("F1: A Distributed SQL Database That Scales", "Arpit Bhayani", "https://drive.google.com/file/d/1noUO2CigYcJV_du_5FSIwSocGkW0NG_L/view?usp=sharing"),
    ("Classifying YouTube Channels: a Practical System", "Arpit Bhayani", "https://drive.google.com/file/d/1xArmuiRC_15oVL3J37UrnPo_fxz2KpNK/view?usp=sharing"),
    ("Talking in Circles: Selective Sharing in Google+", "Arpit Bhayani", "https://drive.google.com/file/d/1eMMTWJD2F063EzPeSES3gc-W37V72CbY/view?usp=sharing"),
    ("Megastore: Providing Scalable, Highly Available Storage for Interactive Services", "Arpit Bhayani", "https://drive.google.com/file/d/1dqZYKAvR13RJWrxePKWha5rU5rPlkUJi/view?usp=sharing"),
    ("Tenzing: A SQL Implementation On The MapReduce Framework", "Arpit Bhayani", "https://drive.google.com/file/d/1nfAAGnKtoEI8lFO-bt84r2-PTutwE2Dp/view?usp=sharing"),
    ("Dremel: Interactive Analysis of Web-Scale Datasets", "Arpit Bhayani", "https://drive.google.com/file/d/1ks_GT7gZXLO8mzVL-0u4-3l60Vr1LyKe/view?usp=sharing"),
    ("Pregel: A System for Large-Scale Graph Processing", "Arpit Bhayani", "https://drive.google.com/file/d/1LTqeoxsQlr9-S4vaFIZN3pI51bmqc1jn/view?usp=sharing"),
    ("Web-Scale Extraction of Structured Data", "Arpit Bhayani", "https://drive.google.com/file/d/1uNT-c0hcP_gB5Ob-59T1lWcOj5WNABtB/view?usp=sharing"),
    ("Leaper: A Learned Prefetcher for Cache Invalidation in LSM-tree based Storage Engines", "Arpit Bhayani", "https://drive.google.com/file/d/1xYuuKYJlDneSwN2Tz2FOXbowVrKwIb45/view?usp=sharing"),
    ("ScaleDB: A Scalable, Asynchronous In-Memory Database", "Arpit Bhayani", "https://drive.google.com/file/d/1AbZ27wwrzOs9Ichjdbtt8d-yYzPO7bfn/view?usp=sharing"),
    ("Segcache: a memory-efficient and scalable in-memory key-value cache for small objects", "Arpit Bhayani", "https://drive.google.com/file/d/11whR-LfZfxieep-qSqIkmuSNDWkgtGps/view?usp=sharing"),
    ("Efficient Search Ranking in Social Networks", "Arpit Bhayani", "https://drive.google.com/file/d/1JigWwsfsLLhRGDsswyb3hN_HEvw3yToi/view?usp=sharing"),
    ("Google News Personalization: Scalable Online Collaborative Filtering", "Arpit Bhayani", "https://drive.google.com/file/d/1gzFUCGhe-9_3XdHbW2ZfZHygJb36yGuo/view?usp=sharing"),
    ("Challenges to Adopting Stronger Consistency at Scale", "Arpit Bhayani", "https://drive.google.com/file/d/1zgdSKdWwHWSN3aASThigfE5nT0Khkou6/view?usp=sharing"),
    ("RadixZip: Linear Time Compression of Token Streams", "Arpit Bhayani", "https://drive.google.com/file/d/1PeQilqwDfvfYw79o4vL59GGEAhAII16p/view?usp=sharing"),
    ("Skip graphs", "Arpit Bhayani", "https://drive.google.com/file/d/1Zyp3B-OBlPNbPyyXouF1fVSrF6Wu1QSp/view?usp=sharing"),
    ("The Bw-Tree: A B-tree for New Hardware Platforms", "Arpit Bhayani", "https://drive.google.com/file/d/10XSVTh3tgyibREz5EsxbRxsc9vzmN8Ge/view?usp=sharing"),
    ("Scaling Up All Pairs Similarity Search", "Arpit Bhayani", "https://drive.google.com/file/d/1K08LaJel9ouK5vygT5IJTtkCd9bpicyQ/view?usp=sharing"),
    ("Detecting Near Duplicates for Web Crawling", "Arpit Bhayani", "https://drive.google.com/file/d/1g5pz1BbCuWQERJbVdDz8WRIY0j8OnHbj/view?usp=sharing"),
    ("Indexing Dataspaces", "Arpit Bhayani", "https://drive.google.com/file/d/1S_zszgSWG_p0D97TJO1hVjBXLMqq-tyW/view?usp=sharing"),
    ("Query logs alone are not enough", "Arpit Bhayani", "https://drive.google.com/file/d/1DGtKfP9iTw54r4CQ8h3LhRAdOIoVKRME/view?usp=sharing"),
    ("Simple Efficient Load Balancing Algorithms for Peer-to-Peer Systems", "Arpit Bhayani", "https://drive.google.com/file/d/1YDuBXvsF0HxPd0uM7g33slfvOsu0wI9f/view?usp=sharing"),
    ("Snapshot-Free, Transparent, and Robust Memory Reclamation for Lock-Free Data Structures", "Arpit Bhayani", "https://drive.google.com/file/d/1PYeZz-CJTh1J8bZ1QeU4b0Ln-zvMCxfr/view?usp=drive_link"),
    ("The Chubby lock service for loosely-coupled distributed systems", "Arpit Bhayani", "https://drive.google.com/file/d/1o5Rto3ex5iDUONNPJf8Wvp43E7wWpdsR/view?usp=sharing"),
    ("Bigtable: A Distributed Storage System for Structured Data", "Arpit Bhayani", "https://drive.google.com/file/d/1o7HrswgtMRYTuDOFsEiAnhpRaYhWxpRt/view?usp=drive_link"),
    ("On-the-fly Sharing for Streamed Aggregation", "Arpit Bhayani", "https://drive.google.com/file/d/156BTit4ZbFdq526_2sdvLBy6WIHV5tmx/view?usp=sharing"),
    ("MapReduce: Simplified Data Processing on Large Clusters", "Arpit Bhayani", "https://drive.google.com/file/d/1fcJP_WE8j0L-QdxQhBSEzkyel8szFzbH/view?usp=sharing"),
    ("How to break software", "Arpit Bhayani", "https://drive.google.com/file/d/1zr4qYypLoaW521NX0WIlV_TXKpa8ZuDG/view?usp=sharing"),
    ("Web Search for a Planet: The Google Cluster Architecture", "Arpit Bhayani", "https://drive.google.com/file/d/1Cs1-ENNZFDcxLh9MB_p7j-IUCboIuwMQ/view?usp=sharing"),
    ("Amazon DynamoDB: A scalable, predictably performant, and fully managed NoSQL database service", "Arpit Bhayani", "https://drive.google.com/file/d/1ztxrZTh3Gn9WWoqprDCU80MjOoXnL6Es/view?usp=sharing"),
    ("Amazon Redshift re-invented", "Arpit Bhayani", "https://drive.google.com/file/d/16Pb3BSWkmNJx0Dato3NVt36nDDKbkkRy/view?usp=sharing"),
    ("Scalable blocking for very large databases", "Arpit Bhayani", "https://drive.google.com/file/d/1RMELaWQ5sPbomHeq5bwwYH79xI6PBiTY/view?usp=sharing"),
    ("Firecracker: Lightweight virtualization for serverless applications", "Arpit Bhayani", "https://drive.google.com/file/d/1u-eQlDjrVn7lzOmX-Cv2si_Wj16H0Z-h/view?usp=drive_link"),
    ("Millions of tiny databases", "Arpit Bhayani", "https://drive.google.com/file/d/16K17SnbgAcFM7j7_qsJJwMX8dYBv9t-n/view?usp=drive_link"),
    ("Amazon Redshift and the Case for Simpler Data Warehouses", "Arpit Bhayani", "https://drive.google.com/file/d/1LwAAnoE2B17AkZ0hU5EBrjwUTcce7qQG/view?usp=drive_link"),
    ("Amazon Aurora: Design considerations for high throughput cloud-native relational databases", "Arpit Bhayani", "https://drive.google.com/file/d/1Aqp80fFRz6A2KiIxoVgB0gYZecoxgZUW/view?usp=drive_link"),
    ("Near-duplicate Question Detection", "Arpit Bhayani", "https://drive.google.com/file/d/1MuqS6WO9wFjOFwtQnp590Tz28o_y6Aco/view?usp=drive_link"),
    ("Striking the right chord: A comprehensive approach to Amazon Music search spell correction", "Arpit Bhayani", "https://drive.google.com/file/d/1SeBP_vLMohz7qlQsOX1pS9hB-8CAGstm/view?usp=drive_link"),
    ("Stage: Query Execution Time Prediction in Amazon Redshift", "Arpit Bhayani", "https://drive.google.com/file/d/1ZkernfuCbAMQOfbfOvK8Gjb9-JJnQOVg/view?usp=sharing"),
    ("A flexible large-scale similar product identification system in e-commerce", "Arpit Bhayani", "https://drive.google.com/file/d/16fqZFuri2WWKM6bfsy-HpWe0hWkdWZdV/view?usp=drive_link"),
    ("Intelligent Scaling in Amazon Redshift", "Arpit Bhayani", "https://drive.google.com/file/d/1E7cb5Ttj21JvI3svJC0QnkhncycX2PS-/view?usp=drive_link"),
    ("Serverless Runtime / Database Co-Design With Asynchronous I/O", "Arpit Bhayani", "https://drive.google.com/file/d/1nuURga5TdctAorXCRPOraIgiLwT0n6S-/view?usp=sharing"),
    ("Predicate Caching: Query-Driven Secondary Indexing for Cloud DataWarehouses", "Arpit Bhayani", "https://drive.google.com/file/d/1K-tWD8-SnQbenEajEHKfPOOL7va-3viA/view?usp=drive_link"),
    ("Query Attribute Recommendation at Amazon Search", "Arpit Bhayani", "https://drive.google.com/file/d/1ItSnpBjjhIyamZFt-82zriHt4Qvo_DBy/view?usp=sharing"),
    ("ROSE: Robust caches for Amazon product search", "Arpit Bhayani", "https://drive.google.com/file/d/13YwkeCc1XwnRVDVkcuE7MKt2r7aqld24/view?usp=drive_link"),
    ("The story of AWS Glue", "Arpit Bhayani", "https://drive.google.com/file/d/1CxK5bTV8ZQgNFe3TI582W9N8PyLa5nK3/view?usp=drive_link"),
    ("DecLog: Decentralized Logging in Non-Volatile Memory for Time Series Database Systems", "Arpit Bhayani", "https://drive.google.com/file/d/1CJwsj-dRcoc_wtkterUQ9l4xtYPOr3On/view?usp=drive_link"),
    ("SILK: Preventing Latency Spikes in LSM Key-Value Stores", "Arpit Bhayani", "https://drive.google.com/file/d/1RCBW70TNXqGowl4I7cPjRJjzpfZqI0rs/view?usp=drive_link"),
    ("Umbra: A Disk-Based System with In-Memory Performance", "Arpit Bhayani", "https://drive.google.com/file/d/1V4sahz-i4Z9wFBsZcj3mHxNAoSXaX53x/view?usp=drive_link"),
    ("Amazon MemoryDB: A fast and durable memory-first cloud database", "Arpit Bhayani", "https://drive.google.com/file/d/1wzSuGMJPShDn5R8SMnam5VXevfeedg7L/view?usp=sharing"),
    ("Take Out the TraChe: Maximizing (Tra)nsactional Ca(che) Hit Rate", "Arpit Bhayani", "https://drive.google.com/file/d/11BQhr3FtKBHrKFvmtNcmOsOnn9NGQ0li/view?usp=drive_link"),
    ("Distributed Transactions at Scale in Amazon DynamoDB", "Arpit Bhayani", "https://drive.google.com/file/d/1Yg2R-wN7KKugx-R4yc8c080XsXtBB0JT/view?usp=drive_link"),
    ("TiDB: A Raft-based HTAP Database", "Arpit Bhayani", "https://drive.google.com/file/d/114Xn8vqP3jrQKNS-9-XdPeLaHMKBO4UV/view?usp=drive_link"),
    ("Kora: A Cloud-Native Event Streaming Platform For Kafka", "Arpit Bhayani", "https://drive.google.com/file/d/1DwH_8_oqgkv8jNkoITqIYPx2-LZnspBx/view?usp=drive_link"),
    ("PolarDB-SCC: A Cloud-Native Database", "Arpit Bhayani", "https://drive.google.com/file/d/1HHEsBWa2MZnJ290ZCAEQK6lNc_X4Vp-2/view?usp=drive_link"),
    ("Epoxy: ACID Transactions Across Diverse Data Stores", "Arpit Bhayani", "https://drive.google.com/file/d/1-fp25FGGIBRqR1MTwG9hUbTm-CMIy9ad/view?usp=drive_link"),
    ("Scalable OLTP in the Cloud: What’s the BIG DEAL?", "Arpit Bhayani", "https://drive.google.com/file/d/1WOXxSBhoDyWe2ZpmOVBD4tcJiFuJTpHq/view?usp=drive_link"),
    ("BonsaiKV: Key-Value Store with Tiered and Heterogeneous Memory System", "Arpit Bhayani", "https://drive.google.com/file/d/15ow-jHUbzi9Hvue8VwYebpcO4wrhbZRW/view?usp=drive_link"),
    ("Automated Unit Test Improvement using Large Language Models at Meta", "Arpit Bhayani", "https://drive.google.com/file/d/1ckfwOOPfg3xTsw2CVoSC8nmlq6LfZoEm/view?usp=drive_link"),
    ("Designing Access Methods: The RUM Conjecture", "Arpit Bhayani", "https://drive.google.com/file/d/1EeZ4vCy8m0Mb06Z-uc-zbtZfQ30ERF6z/view?usp=drive_link"),
    ("Probabilistic Counting Algorithms for Database Applications - Flajolet-Martin", "Arpit Bhayani", "https://drive.google.com/file/d/147IAuDTmHuSS74xd27_HD3NKm14euOPT/view?usp=drive_link"),
    ("Cache-Efficient Top-k Aggregation over High Cardinality Large Datasets", "Arpit Bhayani", "https://drive.google.com/file/d/1fIasc3HCalvsu-CTJp0fyGihiz5xD_UV/view?usp=drive_link"),
    ("SIEVE - an Efficient Turn-Key Eviction Algorithm for Web Caches", "Arpit Bhayani", "https://drive.google.com/file/d/1CMJMCSXW9MrEe5s9i6EQYoTlmzh-fgzk/view?usp=drive_link"),
    ("Vector Database: Storage and Retrieval Technique, Challenge", "Arpit Bhayani", "https://drive.google.com/file/d/1HamJjegLEvLSebnEN-uKLWhQTiZ-UJdd/view?usp=drive_link"),
    ("Panda: Performance Debugging for Databases using LLM Agents", "Arpit Bhayani", "https://drive.google.com/file/d/16zfCBxo-xqhMhrq48dnQmCov-FAn3Lkk/view?usp=drive_link"),
    ("Magnet: A scalable and performant shuffle architecture for Apache Spark", "Arpit Bhayani", "https://drive.google.com/file/d/1xjKIl7SC8tqJeEdN7wGxg956QHRogo2W/view?usp=sharing"),
    ("ZIP: Lazy Imputation during Query Processing", "Arpit Bhayani", "https://drive.google.com/file/d/1yuMg3x4kgZ6eHVoWMgBBttH2C6wsJEa-/view?usp=sharing"),
    ("Anycast as a Load Balancing feature", "Arpit Bhayani", "https://drive.google.com/file/d/1209iTFzMJQDqkPNCneLSp56RyXZqfxoa/view?usp=share_link"),
    ("The Impact of Thread-Per-Core Architecture on Application Tail Latency", "Arpit Bhayani", "https://drive.google.com/file/d/1EJHkuxRJMxK_yFQpUftKW8LaFr2SQDSC/view?usp=sharing"),
    ("TreeLine - An Update-In-Place Key-Value Store for Modern Storage", "Arpit Bhayani", "https://drive.google.com/file/d/1MLkQIO9xqSMc6jv9lbqz32lWBRoTLjT_/view?usp=drive_link"),
    ("Manu: A Cloud Native Vector Database Management System", "Arpit Bhayani", "https://drive.google.com/file/d/1gLl_gSzt6cjnvdPpX40kdaOCiTyMNt4z/view?usp=drive_link"),
    ("Parallelism-Optimizing Data Placement for Faster Data-Parallel Computations", "Arpit Bhayani", "https://drive.google.com/file/d/1rO1FoyU2F0JrNmf5JOZfuPiYmpanwy6b/view?usp=drive_link"),
    ("Faster sorting algorithms discovered using deep reinforcement learning", "Arpit Bhayani", "https://drive.google.com/file/d/16n47YlDxbCXG5qZiu258eK-3y8_Aa9Ru/view?usp=sharing"),
    ("A Relational Model of Data for Large Shared Data Banks", "Arpit Bhayani", "https://drive.google.com/file/d/1_27sKT2kzGCuAL9hEldGO26p_qOhvhS6/view?usp=share_link"),
    ("Improving Language Understanding by Generative Pre-Training", "Arpit Bhayani", "https://drive.google.com/file/d/1yDyKWk4RhC40jbY2evevDnuuxKpIkAxi/view?usp=share_link"),
    ("Language Models are Few-Shot Learners", "Arpit Bhayani", "https://drive.google.com/file/d/1ICUPRGbARL1L_JgMrKfrYQ6xKzh46pjT/view?usp=share_link"),
    ("Attention Is All You Need", "Arpit Bhayani", "https://drive.google.com/file/d/1NI4fHNYauNvH3ynRuhi11Ey5s1-BOpmE/view?usp=share_link"),
    ("Amazon DynamoDB A Scalable, Predictably Performant, and Fully Managed NoSQL Database Service", "Arpit Bhayani", "https://drive.google.com/file/d/1nA7iL9b_WLlQKhuzAV9RlgsrSrWKDsG4/view?usp=share_link"),
    ("Dynamo Amazon’s Highly Available Key-value Store", "Arpit Bhayani", "https://drive.google.com/file/d/1dIX26Vyiva_qxO_5syfMa85ynFpVPIDO/view?usp=share_link"),
    ("The Google File System", "Arpit Bhayani", "https://drive.google.com/file/d/1S_hYRcjdo7aR0ShXuIuK5ePQm2U0FEs2/view?usp=share_link"),
    ("Neural Machine Translation of Rare Words with Subword Units", "Arpit Bhayani", "https://drive.google.com/file/d/1XTvz9HwZ1mlh7D7tfxlILcMgv7IkWkKp/view?usp=share_link"),
    ("The Bloom Paradox: When not to Use a Bloom Filter", "Arpit Bhayani", "https://drive.google.com/file/d/1luxcdZBCxo-ty9sgmEQ1rDs5AF4334-3/view"),
    ("The Deletable Bloom Filter", "Arpit Bhayani", "https://drive.google.com/file/d/1f-LFOroH5WihpfSENXCQJGyM4EWOAgc8/view?usp=share_link"),
    ("Zanzibar - Google's Consistent, Global Authorization System", "Arpit Bhayani", "https://drive.google.com/file/d/1Z3Uzhm-9dhG1DMhyAwDxMhy989N1BIXG/view?usp=share_link"),
    ("Space-Time Trade-offs in Hash Coding with Allowable Errors", "Arpit Bhayani", "https://drive.google.com/file/d/1tWyRo5ofJgMmZpXrSMO6FjfGI0_NFS54/view?usp=share_link"),
    ("Gorilla - A Fast, Scalable, In Memory Time Series Database", "Arpit Bhayani", "https://drive.google.com/file/d/13jFQkD2OmydymjPFLnsvsQUwMwhmynIh/view?usp=sharing"),
    ("Understanding BitTorrent - An Experimental Perspective", "Arpit Bhayani", "https://drive.google.com/file/d/17lvNCfgI2xwMA65VDBcKSPhq0iJqHXVU/view?usp=sharing"),
    ("Exploiting BitTorrent For Fun (But Not Profit)", "Arpit Bhayani", "https://drive.google.com/file/d/13qLIQFaytcTUD0pQEhP_7eeqN_Ryv3bh/view?usp=sharing"),
    ("Rarest First and Choke Algorithms Are Enough", "Arpit Bhayani", "https://drive.google.com/file/d/1GqnGoiQbrbxdn1oVPLVd3z8q-XLaoaIh/view?usp=sharing"),
    ("Implementation of a BitTorrent client - B. Sc. Thesis", "Arpit Bhayani", "https://drive.google.com/file/d/1mCgITghlVle3rFmJzd3Um7B5Wu_k3shb/view?usp=sharing"),
    ("Kademlia - a Peer-to-peer Information System based on XOR Metric", "Arpit Bhayani", "https://drive.google.com/file/d/1EREYP8U1jkxsbsLJvjKhSsz7Scc4xo2c/view?usp=sharing"),
    ("Peer-to-peer networking with BitTorrent", "Arpit Bhayani", "https://drive.google.com/file/d/1VS37P6J3v_trRCHzCOWtS-9lGGcaVq4a/view?usp=sharing"),
    ("Free Riding in BitTorrent is Cheap", "Arpit Bhayani", "https://drive.google.com/file/d/1JEu085WKpy0I-X_enknDs08TH6bnVc0T/view?usp=sharing"),
    ("Go To Statement Considered Harmful", "Arpit Bhayani", "https://drive.google.com/file/d/1qMOCSfTgyPKF6HFS1QFrek_A2pRMmwtK/view?usp=sharing"),
    ("Bitcoin - A Peer-to-Peer Electronic Cash System", "Arpit Bhayani", "https://drive.google.com/file/d/1R0B4ZD67-W4fPmd0EphOXxqWvujZAzHt/view?usp=sharing"),
    ("Understanding Inverse Document Frequency On theoretical arguments for IDF", "Arpit Bhayani", "https://drive.google.com/file/d/11cw9-riCQ5HJ0R2EOHxRijXfV1r76E7Y/view?usp=sharing"),
    ("Isolation Forest", "Arpit Bhayani", "https://drive.google.com/file/d/1yTEFQaEizA-4oPuC4I1NI7XDbu1WXm1W/view?usp=sharing"),
]

ARPIT_NOTES = [
    ("On-demand Container Loading in AWS Lambda", "Arpit Bhayani", "https://arpitbhayani.me/blogs/on-demand-container-loading-in-aws-lambda"),
    ("SQL Has Problems. We Can Fix Them Pipe Syntax In SQL", "Arpit Bhayani", "https://arpitbhayani.me/blogs/sql-has-problems-we-can-fix-them-pipe-syntax-in-sql"),
    ("NanoLog - A Nanosecond Scale Logging System", "Arpit Bhayani", "https://arpitbhayani.me/blogs/nanolog-a-nanosecond-scale-logging-system"),
    ("WTF - The Who to Follow Service at Twitter", "Arpit Bhayani", "https://arpitbhayani.me/blogs/wtf-the-who-to-follow-service-at-twitter"),
]

EXTRA_SECTIONS = {
    "📚 Marc Brooker's Essential Reading": {
        "Essential Leslie Lamport": BROOKER_LAMPORT,
        "Essential Nancy Lynch": BROOKER_LYNCH,
        "Essential Barbara Liskov": BROOKER_LISKOV,
    },
    "🎥 Papers We Love Videos": {
        "All Videos": PWL_VIDEOS,
    },
    "📝 Arpit Bhayani's Papershelf": {
        "Paper Breakdowns (PDFs)": ARPIT_BREAKDOWNS,
        "Paper Notes (Blog)": ARPIT_NOTES,
    },
    "📚 Kafka & Stream Processing": {
        "Papers": [
            ("Kafka: a Distributed Messaging System for Log Processing", "Jay Kreps et al.", "https://notes.stephenholiday.com/Kafka.pdf"),
            ("Kafka versus RabbitMQ", "arXiv 1709.00333", "https://arxiv.org/abs/1709.00333"),
            ("Analysis of Design Patterns and Benchmark Practices in Apache Kafka Event-Streaming Systems", "arXiv 2512.16146", "https://arxiv.org/html/2512.16146"),
            ("On Efficiently Partitioning a Topic in Apache Kafka", "arXiv 2205.09415", "https://arxiv.org/abs/2205.09415"),
            ("Kafka-ML: connecting the data stream with ML/AI frameworks", "arXiv 2006.04105", "https://arxiv.org/abs/2006.04105"),
        ],
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
        # Strip DS:: prefix for display
        display_name = tag_name.replace("DS::", "") if tag_name.startswith("DS::") else tag_name
        post_items = ""
        for p in posts:
            title = esc(p["title"])
            url = esc(p["url"])
            date = p.get("date", "")
            post_items += f'                    <li><a href="{url}" class="block py-1 hover:text-[#C8102E] transition-colors motion-safe:transition-colors"><span class="text-stone-900/70 dark:text-stone-50/70 text-xs tabular-nums mr-2">{date}</span>{title}</a></li>\n'
        tag_id = display_name.lower().replace(" ", "-").replace(",", "")
        tags_html += f"""
                <div class="border border-stone-200 dark:border-stone-800 rounded-sm">
                    <button onclick="toggleCategory('{tag_id}')"
                            class="w-full flex items-center justify-between px-4 py-3 text-left hover:bg-stone-100 dark:hover:bg-stone-800 transition-colors motion-safe:transition-colors focus-visible:ring-2 focus-visible:ring-[#C8102E] focus-visible:outline-none min-h-[44px]"
                            aria-expanded="false" aria-controls="cat-{tag_id}">
                        <span class="text-base font-medium text-stone-900 dark:text-stone-50">{display_name}</span>
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


def load_index_additions():
    """Read papers_index.txt and return (extra_sections, cull_urls)."""
    index_file = os.path.join(SCRIPT_DIR, "papers_index.txt")
    if not os.path.exists(index_file):
        return ({}, set())
    
    with open(index_file) as f:
        content = f.read()
    
    # Extract CULL URLs
    cull_urls = set()
    for line in content.split('\n'):
        if '[CULL]' in line and '|' in line:
            url = line.split('|')[-1].strip()
            cull_urls.add(url)
    
    # Extract ADD sections
    extra_sections = {}
    push_section = None
    for line in content.split('\n'):
        line = line.strip()
        if not line:
            continue
        if line.startswith('--- ADD:'):
            name = line.replace('--- ADD:', '').strip().rstrip('- ').strip()
            # Use a nice display name
            display = f"📖 {name}"
            if display not in extra_sections:
                extra_sections[display] = {"Papers": []}
            push_section = display
        elif line.startswith('[ADD]') and push_section:
            rest = line.replace('[ADD]', '').strip()
            parts = [p.strip() for p in rest.split('|')]
            if len(parts) >= 3:
                title = parts[-3] if len(parts) == 3 else parts[-2]
                url = parts[-1]
                attribution = parts[-2] if len(parts) == 3 else parts[-3]
                extra_sections[push_section]["Papers"].append((title, attribution, url))
    
    # Remove empty
    extra_sections = {k: v for k, v in extra_sections.items() if v["Papers"]}
    return (extra_sections, cull_urls)


def build_html():
    categories = acolyer["categories"]
    
    # Load additions and culls from papers_index.txt
    add_sections, cull_urls = load_index_additions()
    
    # Apply CULLs to Acolyer data
    culled_count = 0
    for tag_name, papers in categories.items():
        original = len(papers)
        filtered = [p for p in papers if p.get("url", "") not in cull_urls]
        categories[tag_name] = filtered
        culled_count += original - len(filtered)
    
    # Merge ADD sections into EXTRA_SECTIONS
    full_extra_sections = dict(EXTRA_SECTIONS)
    full_extra_sections.update(add_sections)
    
    # Split Distributed Systems papers into sub-categories
    ds_subs = split_ds_papers(categories)
    for sub_name, papers in ds_subs.items():
        categories[f"DS::{sub_name}"] = papers
    
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # Build Acolyer sections
    acolyer_html = ""
    for section_name, tag_names in SECTIONS.items():
        acolyer_html += build_acolyer_section(section_name, tag_names, categories)

    # Build extra sections
    extra_html = ""
    for section_name, subsections in full_extra_sections.items():
        extra_html += build_extra_section(section_name, subsections)

    # Stats
    total_acolyer = sum(len(v) for v in categories.values())
    unique_acolyer = len(set(p["url"] for v in categories.values() for p in v))
    total_brooker = sum(len(v) for v in full_extra_sections.get("📚 Marc Brooker's Essential Reading", {}).values())
    total_pwl = sum(len(v) for v in full_extra_sections.get("🎥 Papers We Love Videos", {}).values())
    total_arpit = sum(len(v) for v in full_extra_sections.get("📝 Arpit Bhayani's Papershelf", {}).values())
    total_kafka = sum(len(v) for v in full_extra_sections.get("📚 Kafka & Stream Processing", {}).values())
    total_adds = sum(
        sum(len(subs.get("Papers", [])) for subs in v.values() if "Papers" in v)
        if any("Papers" in sv for sv in v.values()) else sum(len(sv) for sv in v.values())
        for k, v in full_extra_sections.items()
        if k.startswith("📖 ")
    )

    all_section_keys = list(SECTIONS.keys()) + list(full_extra_sections.keys())

    html = f"""<!DOCTYPE html>
<html lang="en" class="scroll-smooth">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="color-scheme" content="light dark">
    <meta name="theme-color" content="#fafaf9" media="(prefers-color-scheme: light)">
    <meta name="theme-color" content="#0c0a09" media="(prefers-color-scheme: dark)">
    <title>Papershelf · Paper Index</title>
    <meta name="description" content="A curated index of CS papers from across the web">
    <meta property="og:title" content="Papershelf">
    <meta property="og:description" content="A curated index of CS papers from across the web">
    <meta property="og:image" content="https://raw.githubusercontent.com/nikhil1raghav/papershelf/main/papershelf-og.png">
    <meta property="og:image:width" content="1424">
    <meta property="og:image:height" content="752">
    <meta property="og:type" content="website">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="Papershelf">
    <meta name="twitter:description" content="A curated index of CS papers from across the web">
    <meta name="twitter:image" content="https://raw.githubusercontent.com/nikhil1raghav/papershelf/main/papershelf-og.png">
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
    <header id="site-header" class="border-b border-stone-200 dark:border-stone-800 sticky top-0 bg-stone-50/95 dark:bg-stone-950/95 backdrop-blur-sm z-10 transition-all motion-safe:transition-all duration-200">
        <div class="max-w-5xl mx-auto px-4 md:px-8 py-6 transition-all motion-safe:transition-all duration-200" id="header-inner">
            <div class="flex flex-col sm:flex-row sm:items-baseline sm:justify-between gap-4" id="header-top">
                <div>
                    <h1 class="text-3xl md:text-4xl font-light tracking-tight text-stone-900 dark:text-stone-50 text-balance transition-all motion-safe:transition-all duration-200" id="header-title">Papershelf</h1>
                    <p class="text-sm text-stone-900/50 dark:text-stone-50/50 mt-1" id="header-subtitle">A curated index of Computer Science paper breakdowns from across the web</p>
                </div>
                <div class="flex items-center gap-4" id="header-count">
                    <span class="text-xs text-stone-900/40 dark:text-stone-50/40 tabular-nums">{total_acolyer + total_brooker + total_pwl + total_arpit + total_kafka + total_adds} entries · {unique_acolyer} Acolyer papers + {total_brooker} Brooker refs + {total_pwl} PWL videos + {total_arpit} Arpit notes + {total_adds} curated additions</span>
                </div>
            </div>
            <!-- Search -->
            <div class="mt-4 relative" id="header-search">
                <input type="text" id="search" placeholder="Search all papers…"
                       class="w-full px-4 py-2 bg-stone-100 dark:bg-stone-900 border border-stone-200 dark:border-stone-800 rounded-sm text-base text-stone-900 dark:text-stone-50 placeholder:text-stone-900/30 dark:placeholder:text-stone-50/30 focus:outline-none focus-visible:ring-2 focus-visible:ring-[#C8102E] transition-colors motion-safe:transition-colors"
                       oninput="filterPapers()">
                <span id="search-count" class="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-stone-900/30 dark:text-stone-50/30 hidden"></span>
            </div>
            <!-- Quick nav -->
            <nav class="mt-4 flex flex-wrap gap-2" aria-label="Jump to section" id="header-nav">
                {''.join(f'<a href="#{s.lower().replace(" ", "-").replace(",", "").replace("&", "and").replace("📚", "").replace("🎥", "").replace("📝", "").replace(":", "").strip()}" class="text-xs px-2 py-1 bg-stone-100 dark:bg-stone-800 border border-stone-200 dark:border-stone-700 rounded-sm hover:border-[#C8102E]/40 hover:text-[#C8102E] transition-colors motion-safe:transition-colors focus-visible:ring-2 focus-visible:ring-[#C8102E] focus-visible:outline-none min-h-[44px] min-w-[44px] inline-flex items-center">{s}</a>' for s in all_section_keys)}
            </nav>
            <!-- Sources -->
            <div class="mt-3 flex flex-wrap gap-3 text-xs text-stone-900/40 dark:text-stone-50/40" id="header-sources">
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
            <p class="text-sm text-stone-900/50 dark:text-stone-50/50 mb-3">Made with love by
                <a href="https://nikhilraghav.xyz/" target="_blank" rel="noopener" class="text-stone-900 dark:text-stone-50 hover:text-[#C8102E] transition-colors motion-safe:transition-colors">Nikhil Raghav</a>
            </p>
            <div class="flex justify-center gap-5 mb-8">
                <a href="https://www.instagram.com/nikhilswe" target="_blank" rel="noopener" aria-label="Instagram" class="text-stone-900/40 dark:text-stone-50/40 hover:text-[#C8102E] transition-colors motion-safe:transition-colors">
                    <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zM12 0C8.741 0 8.333.014 7.053.072 2.695.272.273 2.69.073 7.052.014 8.333 0 8.741 0 12c0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98C8.333 23.986 8.741 24 12 24c3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98C15.668.014 15.259 0 12 0zm0 5.838a6.162 6.162 0 100 12.324 6.162 6.162 0 000-12.324zM12 16a4 4 0 110-8 4 4 0 010 8zm6.406-11.845a1.44 1.44 0 100 2.881 1.44 1.44 0 000-2.881z"/></svg>
                </a>
                <a href="https://www.linkedin.com/in/nikhil1raghav/" target="_blank" rel="noopener" aria-label="LinkedIn" class="text-stone-900/40 dark:text-stone-50/40 hover:text-[#C8102E] transition-colors motion-safe:transition-colors">
                    <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 01-2.063-2.065 2.064 2.064 0 112.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg>
                </a>
                <a href="https://github.com/nikhil1raghav" target="_blank" rel="noopener" aria-label="GitHub" class="text-stone-900/40 dark:text-stone-50/40 hover:text-[#C8102E] transition-colors motion-safe:transition-colors">
                    <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61C4.422 18.07 3.633 17.7 3.633 17.7c-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12"/></svg>
                </a>
                <a href="https://nikhilraghav.xyz/" target="_blank" rel="noopener" aria-label="Website" class="text-stone-900/40 dark:text-stone-50/40 hover:text-[#C8102E] transition-colors motion-safe:transition-colors">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><path d="M2 12h20M12 2a15.3 15.3 0 014 10 15.3 15.3 0 01-4 10 15.3 15.3 0 01-4-10 15.3 15.3 0 014-10z"/></svg>
                </a>
            </div>
            <p class="text-xs text-stone-900/40 dark:text-stone-50/40">
                Papershelf · Generated {now}<br>
                Acolyer papers © Adrian Colyer · Brooker lists © Marc Brooker · PWL videos © Papers We Love · Arpit notes © Arpit Bhayani<br>
                Built as a community index for personal research use
            </p>
        </div>
    </footer>

    <script>
        // Compact header on scroll
        (function() {{
            const header = document.getElementById('site-header');
            const inner = document.getElementById('header-inner');
            const title = document.getElementById('header-title');
            const subtitle = document.getElementById('header-subtitle');
            const count = document.getElementById('header-count');
            const search = document.getElementById('header-search');
            const nav = document.getElementById('header-nav');
            const sources = document.getElementById('header-sources');
            let scrolled = false;

            window.addEventListener('scroll', function() {{
                const isScrolled = window.scrollY > 10;
                if (isScrolled === scrolled) return;
                scrolled = isScrolled;

                if (isScrolled) {{
                    inner.classList.add('py-2');
                    inner.classList.remove('py-6');
                    title.classList.add('text-lg', 'md:text-xl');
                    title.classList.remove('text-3xl', 'md:text-4xl');
                    search.classList.add('mt-1');
                    search.classList.remove('mt-4');
                    subtitle.classList.add('hidden');
                    count.classList.add('hidden');
                    nav.classList.add('hidden');
                    sources.classList.add('hidden');
                }} else {{
                    inner.classList.remove('py-2');
                    inner.classList.add('py-6');
                    title.classList.remove('text-lg', 'md:text-xl');
                    title.classList.add('text-3xl', 'md:text-4xl');
                    search.classList.remove('mt-1');
                    search.classList.add('mt-4');
                    subtitle.classList.remove('hidden');
                    count.classList.remove('hidden');
                    nav.classList.remove('hidden');
                    sources.classList.remove('hidden');
                }}
            }}, {{ passive: true }});
        }})();

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
    print(f"  → 20 fluff posts culled (reading lists, Black Mirror, Fire Swamp, etc.)")
    print(f"Brooker Liskov: {len(BROOKER_LISKOV)} papers")
    print(f"Brooker Lamport: {len(BROOKER_LAMPORT)} papers")
    print(f"Brooker Lynch: {len(BROOKER_LYNCH)} papers")
    print(f"PWL Videos: {len(PWL_VIDEOS)} videos")
    print(f"Arpit Breakdowns: {len(ARPIT_BREAKDOWNS)} PDFs, Notes: {len(ARPIT_NOTES)} blog posts")
    print(f"Kafka papers: 5")
    print(f"Post-2020 additions: 41 papers (LLMs, Vector DBs, Consensus, Rust, etc.)")
    print(f"Software Papers (facundoolano): 144 papers")


if __name__ == "__main__":
    main()
