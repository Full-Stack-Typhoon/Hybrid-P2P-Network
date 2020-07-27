# Hybrid Peer to Peer Distributed File Sharing System

## Overview
Created a P2P file sharing and chat network with a distributed Supernode for fault tolerance along with a client application. Implemented the algorithm for audio and video streaming and downloads from multiple peers.

## Methodology
SuperNode will choose itself as its supernode

## Data Format

{type:'query or data type',data:'query content'}

## Queries

### Search Query:

{type:'search',data:'hello'}

### File List:

{type:'filelist',data:{md5sum:'asdasd',filename:'asdasd'}}

### Make SuperNode:

{type:'makeSuperNode'}

### File Request:

{type:'filerequest',data:{md5sum:'asdasdasd',startByte:12323,endByte:12312}}
