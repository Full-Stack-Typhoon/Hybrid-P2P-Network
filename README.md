# DS Project

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
