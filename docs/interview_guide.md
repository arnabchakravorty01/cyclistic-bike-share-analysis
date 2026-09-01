# Interview guide - how to explain this project

## 30-second version
"I analyzed 3,818,004 Chicago bike-share trips to understand how casual riders differ from annual members. I harmonized inconsistent quarterly schemas, built data-quality checks, handled a daylight-saving timestamp anomaly instead of dropping valid rides, engineered time and station features, and translated the results into conversion recommendations. Casual riders had a 25.8-minute median ride versus 9.8 minutes for members, were much more weekend- and summer-oriented, and had a much higher same-station trip rate. I recommended targeted station/time campaigns and A/B testing rather than making causal claims from trip data alone."

## Questions you should be ready for

**Why did you choose 2019?**  
It was the most recent complete uninterrupted 12-month window among the supplied files. Using an incomplete recent year would introduce missing-month and seasonality bias.

**Why median instead of mean ride duration?**  
The duration distribution contains rare multi-day outliers. Median is robust and better represents a typical trip. I still documented mean sensitivity under 2-hour and 24-hour caps.

**What was the most interesting cleaning issue?**  
Thirteen rides on 3 November had an end local time earlier than the start during the daylight-saving fallback. The source `tripduration` remained positive, so I used it as a fallback instead of deleting valid trips.

**Can you say members are commuters?**  
Not definitively. Their weekday/hour pattern is *consistent with* commute behavior, but the dataset does not contain trip purpose. I avoid converting a behavioral pattern into an unsupported causal claim.

**What would you do next?**  
Refresh on a complete recent year, add weather/events if appropriate, and connect privacy-safe campaign exposure and membership conversion outcomes so the marketing recommendations can be tested experimentally.

**What business recommendation is strongest?**  
Target high-casual stations during casual peak periods because it combines location concentration and timing evidence, making it directly testable through controlled campaign experiments.
