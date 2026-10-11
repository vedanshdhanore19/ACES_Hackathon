# Live orbital data and no-mock-data changes

- Satellite positions in `/api/conjunctions` are propagated with SGP4 from the live CelesTrak GP catalogue.
- The local satellite JSON fallback and hardcoded synthetic satellite positions have been removed.
- If the live catalogue is unavailable or no objects can be propagated, the endpoint returns HTTP 503 instead of inventing markers.
- Proximity records are only created for object pairs whose propagated positions are within 80 km; all pairs are no longer labelled as conjunctions.
- `/api/data-status` checks NASA SSCWeb's live observatory catalogue and CelesTrak connectivity. NASA SSCWeb is not a catalogue of every Earth-orbiting satellite or debris object; it covers supported scientific spacecraft. The broader satellite/debris object catalogue remains CelesTrak.
- SGP4 position components are in the TEME frame. The existing dashboard uses these coordinates for visualization and should not be interpreted as an operational collision probability.

NASA SSCWeb REST docs: https://sscweb.gsfc.nasa.gov/WebServices/REST/
CelesTrak GP catalogue: https://celestrak.org/NORAD/elements/
