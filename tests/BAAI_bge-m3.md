# Benchmark Results: BAAI/bge-m3

## Individual Query Results

### Fundamental Rights

#### Query: equality before law
- **Expected**: 14
- **Predicted**: 14
- **Status**: ✅ PASS

#### Query: abolition of untouchability
- **Expected**: 17
- **Predicted**: 17
- **Status**: ✅ PASS

#### Query: freedom of religion
- **Expected**: 25
- **Predicted**: 25
- **Status**: ✅ PASS

#### Query: minority educational institutions
- **Expected**: 30
- **Predicted**: 30
- **Status**: ✅ PASS

#### Query: right to constitutional remedies
- **Expected**: 32
- **Predicted**: 31C
- **Status**: ❌ FAIL

#### Query: protection against double jeopardy
- **Expected**: 20
- **Predicted**: None
- **Status**: ❌ FAIL

#### Query: forced labour prohibition
- **Expected**: 23
- **Predicted**: 23
- **Status**: ✅ PASS

#### Query: child labour prohibition
- **Expected**: 24
- **Predicted**: 24
- **Status**: ✅ PASS

#### Query: freedom to form associations
- **Expected**: 19
- **Predicted**: 19
- **Status**: ✅ PASS

### Citizenship

#### Query: citizenship by birth
- **Expected**: 5
- **Predicted**: 6
- **Status**: ❌ FAIL

#### Query: migrants from pakistan citizenship
- **Expected**: 6
- **Predicted**: 7
- **Status**: ❌ FAIL

#### Query: foreign citizenship disqualification
- **Expected**: 9
- **Predicted**: 102
- **Status**: ❌ FAIL

#### Query: parliament power over citizenship
- **Expected**: 11
- **Predicted**: 11
- **Status**: ✅ PASS

### Emergency Provisions

#### Query: national emergency proclamation
- **Expected**: 352
- **Predicted**: 352
- **Status**: ✅ PASS

#### Query: suspension of article 19 during emergency
- **Expected**: 358
- **Predicted**: 358
- **Status**: ✅ PASS

#### Query: financial emergency
- **Expected**: 360
- **Predicted**: 360
- **Status**: ✅ PASS

#### Query: parliament power during emergency
- **Expected**: 353
- **Predicted**: 359
- **Status**: ❌ FAIL

#### Query: president rule in state
- **Expected**: 356
- **Predicted**: None
- **Status**: ❌ FAIL

### Reservation & Social Justice

#### Query: reservation in public employment
- **Expected**: 16
- **Predicted**: 16
- **Status**: ✅ PASS

#### Query: reservation for scheduled castes services
- **Expected**: 335
- **Predicted**: None
- **Status**: ❌ FAIL

#### Query: reservation of seats in panchayats
- **Expected**: 243D
- **Predicted**: 243D
- **Status**: ✅ PASS

#### Query: reservation in municipalities
- **Expected**: 243T
- **Predicted**: 243T
- **Status**: ✅ PASS

### Directive Principles

#### Query: uniform civil code
- **Expected**: 44
- **Predicted**: 44
- **Status**: ✅ PASS

#### Query: equal pay for equal work
- **Expected**: 39
- **Predicted**: 39
- **Status**: ✅ PASS

#### Query: free legal aid
- **Expected**: 39A
- **Predicted**: 39
- **Status**: ❌ FAIL

#### Query: protection of environment
- **Expected**: 48A
- **Predicted**: 48A
- **Status**: ✅ PASS

#### Query: separation of judiciary from executive
- **Expected**: 50
- **Predicted**: 50
- **Status**: ✅ PASS

### Rights & Restrictions

#### Query: freedom restrictions
- **Expected**: 19
- **Predicted**: 302
- **Status**: ❌ FAIL

#### Query: state cannot discriminate
- **Expected**: 15
- **Predicted**: 15
- **Status**: ✅ PASS

#### Query: right to life
- **Expected**: 21
- **Predicted**: 41
- **Status**: ❌ FAIL

#### Query: public order restriction speech
- **Expected**: 19
- **Predicted**: 19
- **Status**: ✅ PASS

#### Query: preventive detention
- **Expected**: 22
- **Predicted**: 22
- **Status**: ✅ PASS

### Natural Language Queries

#### Query: can government stop free speech
- **Expected**: 19
- **Predicted**: 19
- **Status**: ✅ PASS

#### Query: can state deny job based on caste
- **Expected**: 16
- **Predicted**: 14
- **Status**: ❌ FAIL

#### Query: detained without lawyer
- **Expected**: 22
- **Predicted**: 22
- **Status**: ✅ PASS

#### Query: court writ powers
- **Expected**: 32
- **Predicted**: 226
- **Status**: ❌ FAIL

### Direct Article References

#### Query: Article 21
- **Expected**: 21
- **Predicted**: 231
- **Status**: ❌ FAIL

#### Query: Article 19 restrictions
- **Expected**: 19
- **Predicted**: 371F
- **Status**: ❌ FAIL

#### Query: Article 356 explanation
- **Expected**: 356
- **Predicted**: 357
- **Status**: ❌ FAIL

#### Query: Explain Article 14
- **Expected**: 14
- **Predicted**: 31A
- **Status**: ❌ FAIL

### Junk Query Rejection Tests

#### Query: how to cook pasta
- **Expected**: None
- **Predicted**: 369
- **Status**: ❌ JUNK FAIL

#### Query: best programming language 2025
- **Expected**: None
- **Predicted**: 343
- **Status**: ❌ JUNK FAIL

#### Query: weather in delhi
- **Expected**: None
- **Predicted**: 130
- **Status**: ❌ JUNK FAIL

#### Query: who is prime minister of japan
- **Expected**: None
- **Predicted**: 75
- **Status**: ❌ JUNK FAIL

#### Query: how to build a startup
- **Expected**: None
- **Predicted**: 3
- **Status**: ❌ JUNK FAIL

#### Query: quantum computing basics
- **Expected**: None
- **Predicted**: None
- **Status**: ✅ JUNK PASS

#### Query: football world cup winner
- **Expected**: None
- **Predicted**: 52
- **Status**: ❌ JUNK FAIL

### Additional Concept Queries

#### Query: reservation
- **Expected**: 16
- **Predicted**: None
- **Status**: ❌ FAIL

#### Query: jobs equality
- **Expected**: 16
- **Predicted**: 16
- **Status**: ✅ PASS

#### Query: religious institution management
- **Expected**: 26
- **Predicted**: 26
- **Status**: ✅ PASS

#### Query: religious tax payment
- **Expected**: 27
- **Predicted**: 27
- **Status**: ✅ PASS

#### Query: religious instruction in schools
- **Expected**: 28
- **Predicted**: 28
- **Status**: ✅ PASS

---

## Performance Summary

| Metric | Value |
|--------|-------|
| Core Accuracy | 27/45 |
| Junk Accuracy | 1/7 |
| Total Queries | 52 |
| Overall Accuracy | 53.85% |

---

## Recall@20 Analysis

| Query | Expected | In Top 20? |
|-------|----------|-----------|
| equality before law | 14 | ✅ YES |
| abolition of untouchability | 17 | ✅ YES |
| freedom of religion | 25 | ✅ YES |
| minority educational institutions | 30 | ✅ YES |
| right to constitutional remedies | 32 | ✅ YES |
| protection against double jeopardy | 20 | ✅ YES |
| forced labour prohibition | 23 | ✅ YES |
| child labour prohibition | 24 | ✅ YES |
| freedom to form associations | 19 | ✅ YES |
| citizenship by birth | 5 | ✅ YES |
| migrants from pakistan citizenship | 6 | ✅ YES |
| foreign citizenship disqualification | 9 | ✅ YES |
| parliament power over citizenship | 11 | ✅ YES |
| national emergency proclamation | 352 | ✅ YES |
| suspension of article 19 during emergency | 358 | ✅ YES |
| financial emergency | 360 | ✅ YES |
| parliament power during emergency | 353 | ✅ YES |
| president rule in state | 356 | ✅ YES |
| reservation in public employment | 16 | ✅ YES |
| reservation for scheduled castes services | 335 | ✅ YES |
| reservation of seats in panchayats | 243D | ✅ YES |
| reservation in municipalities | 243T | ✅ YES |
| uniform civil code | 44 | ✅ YES |
| equal pay for equal work | 39 | ✅ YES |
| free legal aid | 39A | ❌ NO |
| protection of environment | 48A | ✅ YES |
| separation of judiciary from executive | 50 | ✅ YES |
| freedom restrictions | 19 | ✅ YES |
| state cannot discriminate | 15 | ✅ YES |
| right to life | 21 | ✅ YES |
| public order restriction speech | 19 | ✅ YES |
| preventive detention | 22 | ✅ YES |
| can government stop free speech | 19 | ✅ YES |
| can state deny job based on caste | 16 | ✅ YES |
| detained without lawyer | 22 | ✅ YES |
| court writ powers | 32 | ✅ YES |
| Article 21 | 21 | ❌ NO |
| Article 19 restrictions | 19 | ✅ YES |
| Article 356 explanation | 356 | ✅ YES |
| Explain Article 14 | 14 | ✅ YES |
| reservation | 16 | ❌ NO |
| jobs equality | 16 | ✅ YES |
| religious institution management | 26 | ✅ YES |
| religious tax payment | 27 | ✅ YES |
| religious instruction in schools | 28 | ✅ YES |

---

## Final Metrics

**Recall@20: 93.33%**

---

## Strategic Conclusion

**STRATEGY**: Recall is the bottleneck. Upgrade to BGE-M3 before adding Reranker.
