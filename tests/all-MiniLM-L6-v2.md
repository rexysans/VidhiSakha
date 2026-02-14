# Benchmark Results: all-MiniLM-L6-v2

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
- **Predicted**: 26
- **Status**: ❌ FAIL

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
- **Predicted**: 20
- **Status**: ✅ PASS

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
- **Predicted**: 26
- **Status**: ❌ FAIL

### Citizenship

#### Query: citizenship by birth
- **Expected**: 5
- **Predicted**: 8
- **Status**: ❌ FAIL

#### Query: migrants from pakistan citizenship
- **Expected**: 6
- **Predicted**: 7
- **Status**: ❌ FAIL

#### Query: foreign citizenship disqualification
- **Expected**: 9
- **Predicted**: 191
- **Status**: ❌ FAIL

#### Query: parliament power over citizenship
- **Expected**: 11
- **Predicted**: 11
- **Status**: ✅ PASS

### Emergency Provisions

#### Query: national emergency proclamation
- **Expected**: 352
- **Predicted**: 354
- **Status**: ❌ FAIL

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
- **Predicted**: 250
- **Status**: ❌ FAIL

#### Query: president rule in state
- **Expected**: 356
- **Predicted**: 356
- **Status**: ✅ PASS

### Reservation & Social Justice

#### Query: reservation in public employment
- **Expected**: 16
- **Predicted**: 16
- **Status**: ✅ PASS

#### Query: reservation for scheduled castes services
- **Expected**: 335
- **Predicted**: 243T
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
- **Predicted**: 26
- **Status**: ❌ FAIL

#### Query: state cannot discriminate
- **Expected**: 15
- **Predicted**: 15
- **Status**: ✅ PASS

#### Query: right to life
- **Expected**: 21
- **Predicted**: 21
- **Status**: ✅ PASS

#### Query: public order restriction speech
- **Expected**: 19
- **Predicted**: 194
- **Status**: ❌ FAIL

#### Query: preventive detention
- **Expected**: 22
- **Predicted**: 22
- **Status**: ✅ PASS

### Natural Language Queries

#### Query: can government stop free speech
- **Expected**: 19
- **Predicted**: None
- **Status**: ❌ FAIL

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
- **Predicted**: 139
- **Status**: ❌ FAIL

### Direct Article References

#### Query: Article 21
- **Expected**: 21
- **Predicted**: 21
- **Status**: ✅ PASS

#### Query: Article 19 restrictions
- **Expected**: 19
- **Predicted**: 31C
- **Status**: ❌ FAIL

#### Query: Article 356 explanation
- **Expected**: 356
- **Predicted**: 264
- **Status**: ❌ FAIL

#### Query: Explain Article 14
- **Expected**: 14
- **Predicted**: 31C
- **Status**: ❌ FAIL

### Junk Query Rejection Tests

#### Query: how to cook pasta
- **Expected**: None
- **Predicted**: None
- **Status**: ✅ JUNK PASS

#### Query: best programming language 2025
- **Expected**: None
- **Predicted**: None
- **Status**: ✅ JUNK PASS

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
- **Predicted**: None
- **Status**: ✅ JUNK PASS

#### Query: quantum computing basics
- **Expected**: None
- **Predicted**: None
- **Status**: ✅ JUNK PASS

#### Query: football world cup winner
- **Expected**: None
- **Predicted**: None
- **Status**: ✅ JUNK PASS

### Additional Concept Queries

#### Query: reservation
- **Expected**: 16
- **Predicted**: 243T
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
| Core Accuracy | 26/45 |
| Junk Accuracy | 5/7 |
| Total Queries | 52 |
| Overall Accuracy | 59.62% |

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
| freedom to form associations | 19 | ❌ NO |
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
| public order restriction speech | 19 | ❌ NO |
| preventive detention | 22 | ✅ YES |
| can government stop free speech | 19 | ✅ YES |
| can state deny job based on caste | 16 | ✅ YES |
| detained without lawyer | 22 | ✅ YES |
| court writ powers | 32 | ✅ YES |
| Article 21 | 21 | ✅ YES |
| Article 19 restrictions | 19 | ❌ NO |
| Article 356 explanation | 356 | ❌ NO |
| Explain Article 14 | 14 | ❌ NO |
| reservation | 16 | ✅ YES |
| jobs equality | 16 | ✅ YES |
| religious institution management | 26 | ✅ YES |
| religious tax payment | 27 | ✅ YES |
| religious instruction in schools | 28 | ✅ YES |

---

## Final Metrics

**Recall@20: 86.67%**

---

## Strategic Conclusion

**STRATEGY**: Recall is the bottleneck. Upgrade to BGE-M3 before adding Reranker.
