# RoboCup CI – 1001 game a night

### General Flow

```plantuml
'!include myStyle.uml

skinparam backgroundcolor transparent
'skinparam dpi 300

skinparam classArrowColor black
skinparam classArrowFontName Arial
' skinparam classAttributeFontColor #280000
skinparam classAttributeFontName Arial
skinparam classAttributeIconSize 0
skinparam classBackgroundColor #FFCD9B/#FFFDD8
skinparam classBorderColor #99795C 
skinparam classBorderThickness .8
skinparam classFontName Arial
skinparam classFontSize 11
skinparam classFontStyle bold
skinparam classStereotypeFontName ArialNarrow

skinparam objectArrowColor black
skinparam objectArrowFontName Arial
' skinparam objectAttributeFontColor #280000
skinparam objectAttributeFontName Arial
skinparam objectBackgroundColor #FFF0B4/#FFFFFF
skinparam objectBorderColor #99795C 
skinparam objectBorderThickness .8
skinparam objectFontName Arial
skinparam objectFontSize 11
skinparam objectFontStyle bold
skinparam objectStereotypeFontName ArialNarrow

skinparam sequence {
	ArrowColor #424242
	LifeLineBorderColor #3D6652
	LifeLineBackgroundColor #C2E3D3
	
	ParticipantBorderColor #3D6652
	ParticipantBackgroundColor #C2E3D3/#FFFFFF
	ParticipantFontName Arial
	ParticipantFontSize 11
'	ParticipantFontColor #A9DCDF
	
	ActorBorderColor #424242
	ActorBackgroundColor #FFF0B4/#FFFFFF
	ActorFontColor #424242
	ActorFontSize 11
	ActorFontName Arial

'	ArrowFontColor
	ArrowFontSize 11
'	ArrowFontStyle
	ArrowFontName Arial
	GroupingBorderThickness .1
'	GroupingFontColor
	GroupingFontSize 11
	GroupingFontStyle plain
	GroupingFontName Arial
'	GroupingHeaderFontColor
	GroupingHeaderFontSize 11
	GroupingHeaderFontStyle plain
	GroupingHeaderFontName Arial
}

skinparam noteFontColor black
skinparam noteFontSize 9
' skinparam noteFontStyle
skinparam noteFontName Arial
skinparam noteBackgroundColor #EEEEEE
skinparam noteBorderColor #000000

' hide empty members
' hide empty attributes
hide empty methods
hide footbox
hide circle


 -> RobocupUser : cronjob
activate RobocupUser
RobocupUser -> gitlab : getLatestSuccessfullBuild
RobocupUser -> gitlab : getLatestSuccessfullCommitID
note right of RobocupUser
git's CommitID is necessary to group all match results played with same version of code
end note

group Parallel [20 Computers]
  create HLM
  RobocupUser -> HLM : start
  activate HLM
  create rcssserver
  HLM -> rcssserver : execute 50 matches
'  activate rcssserver
'  destroy rcssserver

  create PythonAnalyzer
  HLM -> PythonAnalyzer : analyze log files (rcg/rcl)
  activate PythonAnalyzer
  PythonAnalyzer -> Node.js : upload json
  destroy PythonAnalyzer
  deactivate HLM
end

RobocupUser -> Node.js : getLastNightsOutliers
activate Node.js

create OutlierFinder
Node.js -> OutlierFinder : findLastNightsOutliers
activate OutlierFinder
OutlierFinder --> Node.js: outliers
destroy OutlierFinder

Node.js --> RobocupUser : outliers
deactivate Node.js
RobocupUser -> Node.js : upload outlier rcg/rcl
activate Node.js
deactivate Node.js
deactivate RobocupUser
```
