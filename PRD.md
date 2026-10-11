# Product Requirements Document (PRD)

## Project Name
Orbital Conjunction & Space Traffic Risk Engine

## Problem Statement
Low Earth Orbit (LEO) is densely populated with active satellites and orbital debris. Satellite operators face hundreds of proximity alerts daily, risking fuel waste on unnecessary maneuvers. Atmospheric drag caused by solar flare heating introduces unpredictable orbital decay, rendering static deterministic predictions inaccurate.

## Primary Objective
Build an automated, high-throughput space traffic monitoring service that ingests live orbital catalog feeds (TLEs) and space weather data, propagates trajectories across a 24-hour window, detects close approaches (conjunctions), and dynamically adjusts collision probability scores based on real-time atmospheric drag uncertainty.

## Core Features
1. Live TLE Ingestion: Automatically pull active satellite orbital parameters from CelesTrak.
2. Space Weather Ingestion: Ingest real-time solar radio flux index from NOAA SWPC.
3. Rapid Conjunction Screening: Perform 3D Euclidean distance filtering across all satellite pairs over 24 hours.
4. Drag Uncertainty Modeling: Scale the covariance error ellipse along the velocity vector using the solar flux parameter.
5. Interactive 3D Tactical Map: Render Earth with satellite positions, highlight high-risk pairs in pulsing red, and provide an interactive Solar Flux slider to simulate solar storm impact live.  