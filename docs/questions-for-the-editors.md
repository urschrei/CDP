# Questions for the editors

These questions need the tablets, the photographs or the sign lists to answer. The data alone cannot answer them. Write each answer under its question.

A path such as `/tablets/487` is a page of the CDP site: add it to the address of the site. A path such as `/media/instance/I_1103765344552.jpg` is a photograph of a sign. [Schema and data questions](schema-and-data-questions.md) records the findings behind the questions.

The list describes the data on 13 September 2026.

## Sign lists

### 1. Which list is aBZL?

Is the column aBZL Mittermayer's *Altbabylonische Zeichenliste*, or Borger's *Assyrisch-babylonische Zeichenliste*?

- The highest aBZL number in the data is 480, the last number of Mittermayer's list. Borger's list has 598 numbers.
- The spreadsheet `csvs/signs_from_instances.xls` has one column for Borger ABZ and a different column for aBZL.
- The site links aBZL numbers to Mittermayer's numbers in the Oracc Sign List.

Answer:

### 2. Which lists are HA and Labat?

What are the full titles of the lists HA and Labat? The site links both to one numbering of the Oracc Sign List, which Deimel's *Šumerisches Lexikon*, Labat's *Manuel d'épigraphie akkadienne* and Ellermeier and Studt's *Handbuch Assur* share. In 1,227 of the 1,436 CDP records with both numbers, the HA number and the Labat number are the same.

Answer:

### 3. What are the full titles of the lists Emar and Hinke?

Answer:

### 4. Does the CDP need the lists Rosengarten and LKA?

`csvs/signs_from_instances.xls` has empty columns for Rosengarten and LKA. The CDP does not have these lists.

Answer:

### 5. What are the Description names?

The CDP records have names from a spreadsheet column with the heading Description, for example `ILIMMU`. They look like sign names, not descriptions. From which source are they?

Answer:

## CDP records

### 6. What makes these records different?

The records in each group are the same in all their values. If nothing makes them different, we can remove the copies.

| Sign | Sign page | Records |
| --- | --- | --- |
| ADDU₂ | `/signs/29316` | 1196, 1197 |
| ALIMₓ | `/signs/29368` | 1277, 1278 |
| DUBAL₃ | `/signs/29634` | 1782, 1783 |
| DUBAL₄ | `/signs/29635` | 1784, 1785 |
| DUL | `/signs/29647` | 1808, 1809, 1810 |
| DUN₃ | `/signs/29655` | 1823, 1824 |
| GALAM | `/signs/29857` | 2143, 2144 |
| GIDIM₄ | `/signs/29960` | 2272, 2273 |

Answer:

### 7. What are these form descriptions?

The only copy of these form descriptions is a database dump of 2013, which replaced each character that is not ASCII with `_`. Where the data have names with the same letters, the table gives them as possible values. What is each form description?

| Record | Sign | Sign page | Form description in the dump | Possible values |
| --- | --- | --- | --- | --- |
| 385 | \|LU₂×(SIG₂.BU)\| | `/signs/28544` | `\|LU__SIK_+BU\|` | |
| 792 | 2(DIŠ@t) | `/signs/28948` | `2(di_@t)` | |
| 908 | 3(ŠAR₂)1 | `/signs/29064` | `3(_ar_)3(_ar_@c)` | |
| 1145 | ABLAL | `/signs/29291` | `\|LAGAB_A+LAL\|` | |
| 1212 | AGAR₃ | `/signs/29325` | `\|LAGAB_A+GAR\|` | |
| 1295 | AMAŠ | `/signs/29381` | `\|DAG.KISIM__LU+MA__\|` | |
| 1342 | ARATTA | `/signs/29407` | `\|LAM_KUR+RU\|` | |
| 1517 | BARA₆ | `/signs/29507` | `\|LAGAB_ME+EN\|` | |
| 1525 | BER₆ | `/signs/29514` | `\|_A__U+A\|` | |
| 1549 | BUBBU | `/signs/29531` | `\|LAGAB_U+U+U.LAGAB_U+U+U\|` | |
| 1554 | BUL | `/signs/29535` | `\|LAGAB_U+U+U\|` | |
| 1559 | BUNₓ | `/signs/29540` | `\|URU_MIN+IM\|` | |
| 1561 | BUNₓ | `/signs/29540` | `\|EZEN~b_A_\| -- need to sort out EZEN~a/b` | |
| 1753 | DINIG₂ | `/signs/29617` | `\|LU__ME+EN\|` | |
| 1784 | DUBAL₄ | `/signs/29635` | `\|LU__KAD_\|` | \|LU₂×KAD₂\|, \|LU₂×KAD₃\| |
| 1785 | DUBAL₄ | `/signs/29635` | `\|LU__KAD_\|` | \|LU₂×KAD₂\|, \|LU₂×KAD₃\| |
| 1931 | EMEDA₃ | `/signs/29720` | `\|UM_ME+DA\|` | |
| 1937 | EMEGARₓ | `/signs/29724` | `\|KA_ME+GAR\|` | |
| 1938 | EMEGARGARₓ | `/signs/29725` | `\|KA_ME+GAR+GAR+RA\|` | |
| 1940 | EMENGI | `/signs/29727` | `\|KA_ME+GI\|` | |
| 1996 | ERIMₓ | `/signs/29769` | `\|AB_U+U+U\|` | |
| 2038 | ESIRHA | `/signs/29800` | `\|LAGAB_KUL+HI+A\|` | |
| 2423 | GUERIŠI | `/signs/30033` | `\|GU__SAL+TUG_\|` | |
| 2510 | HARA₅ | `/signs/30092` | `\|DAG.KISIM__U_+GIR_\|` | |
| 2511 | HARA₅ | `/signs/30092` | `\|DAG.KISIM__U_+GIR_\|` | |
| 2512 | HARA₅ | `/signs/30092` | `\|DAG.KISIM__U_+GIR_\|` | |
| 2614 | ILDAG₂ | `/signs/30164` | `\|GUD_A+KUR\|` | |
| 2634 | IMMINTE | `/signs/30182` | `\|KA_ME+TE\|` | |
| 2667 | ITI | `/signs/30205` | `\|UD_U+U+U\|` | |
| 2668 | ITI.DU | `/signs/30206` | `\|UD_U+U+U.DU\|` | |
| 2671 | ITI₇ | `/signs/30209` | `\|UD_U+U+U.AN._E_.KI\|` | |
| 2678 | KA×(ME.ME) | `/signs/30215` | `\|KA_ME+ME\|` | |
| 2679 | KA×(MI.NUNUZ) | `/signs/30216` | `\|KA_MI+NUNUZ\|` | |
| 2804 | KIR₇ | `/signs/30297` | `\|NIM_GAR+GAN_@t\|` | |
| 2866 | KUNGA₂ | `/signs/30335` | `\|_U_.3xAN\|` | |
| 3049 | LUGUD₄ | `/signs/30445` | `\|LAGAR__E+SUM\|` | |
| 3087 | MAŠ.EN | `/signs/30469` | `\|MA_+EN\|` | |
| 3101 | MASSA₂ | `/signs/30483` | `\|DAG.KISIM__A+MA_\|` | |
| 3102 | MASSA₂ | `/signs/30483` | `\|DAG.KISIM__A+MA_\|` | |
| 3106 | MEₓ | `/signs/30485` | `\|LAGAB__ITA+GI_+ERIN_\|` | |
| 3115 | ME₉ | `/signs/30489` | `\|LAGAB__ITA@t+GI_\|` | |
| 3118 | MEDU | `/signs/30492` | `\|KA_ME+DU\|` | |
| 3123 | MELEₓ | `/signs/30496` | `\|KA_GAR+_A_+A\|` | |
| 3200 | MURₓ | `/signs/30541` | `\|UD_U+U+U@g\|` | |
| 3205 | MURU₄ | `/signs/30546` | `\|UR__U_+A_\|` | |
| 3311 | NIGRU | `/signs/30616` | `\|KA_AD+KU_\|` | |
| 3339 | NINDAMEKAR | `/signs/30638` | `\|NINDA__ME+GAN_@t\|` | |
| 3405 | NUNUZ.AB₂×(BULUG₂.GUG₂) | `/signs/30670` | `\|NUNUZ.AB__BULUG_+GUG_\|` | |
| 3406 | NUNUZ.AB₂×(BULUG₂.GUG₂) | `/signs/30670` | `\|NUNUZ.AB__BULUG_+GUG_\|` | |
| 3407 | NUNUZ.AB₂×(GUG₂.BULUG₂) | `/signs/30671` | `\|NUNUZ.AB__GUG_+BULUG_\|` | |
| 3409 | NUNUZ.KISIM₅×(LU₃.PAP.PAP) | `/signs/30673` | `\|NUNUZ.KISIM__LU_+PAP+PAP\|` | |
| 3491 | RAPIKU | `/signs/30725` | `\|DAG.KISIM__PAP+PAP\|` | |
| 3507 | SAₓ | `/signs/30738` | `\|NINDA__A_+A_\|` | |
| 3509 | SAₓ | `/signs/30738` | `\|NINDA___E+A_\|` | |
| 3510 | SAₓ | `/signs/30738` | `\|NINDA___E+A_+A_\|` | |
| 3511 | SAₓ | `/signs/30738` | `\|NINDA___E+A.AN\|` | |
| 3561 | SAGKURUN | `/signs/30771` | `\|DIN.KASKAL.GA_AN.DI_\|` | |
| 3582 | ŠAKIRₓ | `/signs/30784` | `\|URU_MIN+NI\|` | |
| 3583 | ŠAKIRₓ | `/signs/30784` | `\|URU_MIN+NI+GA\|` | |
| 3614 | ŠAMₓ | `/signs/30792` | `\|NINDA___E+A+AN\|` | |
| 3638 | SAMAN | `/signs/30799` | `E__` | EŠ₂, EŠ₅, EŠ₆, E₁₂ |
| 3669 | ŠARGALDIŠ | `/signs/30818` | `\|_AR__GAL+DI_\|` | |
| 3670 | ŠARGALMIN | `/signs/30819` | `\|_AR__GAL+MIN\|` | |
| 3673 | ŠARUMINₓ | `/signs/30822` | `\|HI_U+U\|` | |
| 3697 | SED₃ | `/signs/30834` | `\|ZA.MU__.DI\|` | \|ZA.MUŠ₂.DI\|, \|ZA.MUŠ₃.DI\| |
| 3732 | ŠERIMSUR | `/signs/30854` | `\|LAGAB__E+SUM\|` | |
| 3866 | ŠU₂.ZI₃ | `/signs/30942` | `\|_U_+ZI_\|` | |
| 3883 | ŠU₆ | `/signs/30949` | `\|LAGAB__U_+_U_\|` | |
| 4138 | U₈ | `/signs/31115` | `\|LAGAB_GUD+GUD\|` | |
| 4141 | UBIₓ | `/signs/31118` | `\|_E+SUHUR\|` | |
| 4144 | UBUR₄ | `/signs/31121` | `\|DAG.KISIM__IR+LU\|` | |
| 4159 | UD.AB×EŠ | `/signs/31124` | `\|UD.AB_U+U+U\|` | |
| 4172 | UDUL₄ | `/signs/31134` | `\|PA.DAG.KISIM__LU+MA__\|` | |
| 4198 | UGRA | `/signs/31148` | `\|LAGAB_U_+A_\|` | |
| 4290 | UR₂×(A.NA) | `/signs/31198` | `\|UR__A+NA\|` | |
| 4291 | UR₂×(U₂.BI) | `/signs/31199` | `\|UR__U_+BI\|` | |
| 4334 | URU×UL | `/signs/31222` | `\|URU_U+GUD\|` | |
| 4348 | URUM | `/signs/31232` | `\|NINDA__U_+A_\|` | |
| 4351 | URUM₉ | `/signs/31235` | `\|UR__A+HA\|` | |
| 4413 | UʾU | `/signs/31276` | `\|LAGAB_(GUD+GUD).A\|` | |
| 4469 | ZANABAL | `/signs/31309` | `\|LU__LA+A_\|` | |
| 4470 | ZANABAL₂ | `/signs/31310` | `\|LU__KAD_+A_\|` | |
| 4471 | ZANABAL₃ | `/signs/31311` | `\|LU__SI+A_\|` | |

Answer:

### 8. Were three records removed on purpose?

The dump of 2013 has three records that the import of 2014 did not copy. The dump replaced the characters of their sign name. Were they removed on purpose?

| Sign-list numbers | Names in the dump |
| --- | --- |
| MesZL 758, ELLes 376, LAK 769, HA 484a | `\|LAGAB_AN\|` |
| ELLes 109, LAK 185, ZATU N-58 | `2(A_@t)` |
| LAK 193 | `5(A_@t)` |

Answer:

## Tablets

### 9. Which ruler is on these tablets?

The publication number of each tablet is the number of a different reign from the reign of its ruler.

| Tablet | Page | Publication | Ruler in the data | Reign of the publication number |
| --- | --- | --- | --- | --- |
| BM_91082 | `/tablets/569` | RIME.4.4.3.1 | Sin-gamil (Diniktum), E.4.13.2 | Sin-gamil (Uruk), E.4.4.3 |
| BM_96952 | `/tablets/549` | RIME.4.3.6.11 | Samsu-iluna, E.4.3.7 | Hammu-rapi (Babylon), E.4.3.6 |

For BM_91082, the comment in `csvs/ruler_name_matching.xlsx` also gives Uruk. CDLI gives `RIME 4.04.03.x2001, ex. 01` for BM_91082 (P429914), and the same number as the data for BM_96952 (P431849).

Answer:

### 10. Are these publication numbers correct?

The rulers are kings of Ur III, but the publication numbers begin with RIME 4, the volume of the Old Babylonian period. E.4.1.1 is Ishbi-Erra and E.4.1.2 is Shu-ilishu. Are the correct numbers RIME 3/2.1.1 and RIME 3/2.1.2?

| Tablet | Page | Publication | Ruler |
| --- | --- | --- | --- |
| BM_90010 | `/tablets/583` | RIME.4.1.1.33 | Ur-Nammu |
| BM_90011 | `/tablets/584` | RIME.4.1.1.4 | Ur-Nammu |
| BM_90015 | `/tablets/585` | RIME.4.1.1.33 | Ur-Nammu |
| BM_90016 | `/tablets/586` | RIME.4.1.1.35 | Ur-Nammu |
| BM_90017 | `/tablets/568` | RIME.4.1.2.39 | Shulgi |

For all five tablets, CDLI gives RIME 3/2.1.1 or RIME 3/2.1.2 with the same text number, for example `RIME 3/2.01.01.33, ex. 03` for BM_90010 (P226645).

Answer:

### 11. Esarhaddon or Ashurbanipal?

These letters refer to both Esarhaddon and Ashurbanipal. The spreadsheet of ruler names gives `Esarhaddon or Assurbanipal`. Must each letter have one ruler? If so, which?

| Tablet | Page | Publication |
| --- | --- | --- |
| 81_2-4_287 | `/tablets/671` | SAA 8, 70 |
| DT_148 | `/tablets/673` | SAA 8, 16 |
| K_1326 | `/tablets/676` | SAA 8, 79 |
| K_696 | `/tablets/668` | SAA 8, 10 |
| K_697 | `/tablets/674` | SAA 8, 15 |
| K_773 | `/tablets/675` | SAA 8, 17 |
| K_788 | `/tablets/667` | SAA 8, 9 |
| K_8432 | `/tablets/669` | SAA 8, 63 |
| K_984 | `/tablets/670` | SAA 8, 67 |
| Rm_203 | `/tablets/672` | SAA 8, 11 |

Answer:

### 12. Year or eponym?

83-1-18_287 (`/tablets/487`, SAA 8, 8) has the year 658 BC and the eponym Labasi. The eponym of 658 BC in the data is Sha-Nabu-shu. Which is correct?

Answer:

### 13. Which reign is the reign of a tablet?

Esarhaddon and Ashurbanipal each have an Assyrian and a Babylonian reign, for example A.0.113 and B.6.32 for Ashurbanipal. The notes on the ruler names say that the tablets belong to the Assyrian reign. At present, a tablet refers to a ruler, not to a reign. Must a tablet refer to a reign?

Answer:

### 14. Which sub-period have the kings of Alalakh?

The reigns B.20.1 to B.20.4 (Idrimi, Addu-nirari, Niqmepuh and Ilim-ilimma II) are Middle Babylonian, with no sub-period. The sub-periods of Middle Babylonian are Kassite and Post-Kassite.

Answer:

### 15. Where is the data from Amarna?

The notes on the ruler names say that the new data adds the city Amarna, in Egypt. The city is in the data, but no tablet refers to it.

Answer:

## Positions of signs

### 16. What is the line of these signs?

Only signs on seal impressions have no line. These 32 signs are not on seal impressions, but have no line.

| Tablet | Page | Sign | Surface | Column | Photograph |
| --- | --- | --- | --- | --- | --- |
| 82_5-22_130 | `/tablets/470` | GI | | | `/media/instance/I_1103765344552.jpg` |
| BM_113352 | `/tablets/536` | AŠ | be | | `/media/instance/I_1191939762718.jpg` |
| BM_113352 | `/tablets/536` | 1+A₂ | be | | `/media/instance/I_1191941745890.jpg` |
| BM_113352 | `/tablets/536` | UGU | be | | `/media/instance/I_1191940222953.jpg` |
| BM_113352 | `/tablets/536` | TI | be | | `/media/instance/I_1192027642156.jpg` |
| BM_113352 | `/tablets/536` | MES | be | | `/media/instance/I_1191942314562.jpg` |
| BM_113352 | `/tablets/536` | HI | be | | `/media/instance/I_1191940416343.jpg` |
| BM_113352 | `/tablets/536` | A₂ | be | | `/media/instance/I_1192028450593.jpg` |
| BM_38120 | `/tablets/502` | GI | | | `/media/instance/I_1157290734984.jpg` |
| BM_38622 | `/tablets/652` | NU | rev | iv | `/media/instance/I_1172577198625.jpg` |
| BM_68332 | `/tablets/628` | AK | catchline | iv | `/media/instance/I_1163694228984.jpg` |
| BM_68332 | `/tablets/628` | LUM | catchline | iv | `/media/instance/I_1163694716046.jpg` |
| BM_68332 | `/tablets/628` | E | catchline | iv | `/media/instance/I_1163694423015.jpg` |
| K_12032 | `/tablets/484` | NU | catchline | | `/media/instance/I_1172767678968.jpg` |
| K_14895 | `/tablets/473` | GAR | a | | `/media/instance/I_1152728581140.jpg` |
| K_14895 | `/tablets/473` | GIŠ | a | | `/media/instance/I_1152729746968.jpg` |
| K_14895 | `/tablets/473` | ZA | a | | `/media/instance/I_1152729058828.jpg` |
| K_197 | `/tablets/481` | AK | rev | iv | `/media/instance/I_1160573865046.jpg` |
| K_197 | `/tablets/481` | HI | rev | iv | `/media/instance/I_1160576040000.jpg` |
| K_197 | `/tablets/481` | TE | rev | iv | `/media/instance/I_1160574638937.jpg` |
| K_197 | `/tablets/481` | MAN | rev | iv | `/media/instance/I_1160575490359.jpg` |
| K_197 | `/tablets/481` | KUR | rev | iv | `/media/instance/I_1160575661281.jpg` |
| K_197 | `/tablets/481` | KI | rev | iv | `/media/instance/I_1160576280390.jpg` |
| K_197 | `/tablets/481` | E | rev | iv | `/media/instance/I_1160574764078.jpg` |
| K_197 | `/tablets/481` | A | rev | iv | `/media/instance/I_1160574383796.jpg` |
| K_197 | `/tablets/481` | A | rev | iv | `/media/instance/I_1160575134609.jpg` |
| K_39 | `/tablets/483` | DIVIDING_SIGN | aas | | `/media/instance/I_1169136552843.jpg` |
| K_39 | `/tablets/483` | UM | rev | iv | `/media/instance/I_1171399651781.jpg` |
| K_39 | `/tablets/483` | UL | rev | iv | `/media/instance/I_1171388146765.jpg` |
| K_39 | `/tablets/483` | NU | rev | iv | `/media/instance/I_1171399386796.jpg` |
| K_39 | `/tablets/483` | E₂ | colophon | | `/media/instance/I_1171570112134.jpg` |
| K_39 | `/tablets/483` | AN | rev | iv | `/media/instance/I_1171399219125.jpg` |

Answer:

### 17. What do the surfaces a, be and aas mean?

| Surface | Tablet | Page | Publication | Signs |
| --- | --- | --- | --- | --- |
| a | BM_40127 | `/tablets/472` | MSL 16 p. 49 | 8 |
| a | K_14895 | `/tablets/473` | MSL 16 p. 49 | 3 |
| a | W_18202_25 | `/tablets/662` | AUWE 5, 129 | 34 |
| be | BM_113352 | `/tablets/536` | unpublished | 7 |
| aas | K_39 | `/tablets/483` | MSL 16 p. 117 | 1 |

`a` is the only surface of the signs on its three tablets. `be` is possibly the bottom edge. Is `a` side A of a fragment whose obverse and reverse are not known?

Answer:

## Languages

### 18. Do these signs have no language, or is the language missing?

365 signs have no language. For each tablet, the table gives the number of signs without a language and the number of all its signs. Most are on Old Babylonian school tablets from Nippur.

| Tablet | Page | Publication | Genre | City | Without language | All |
| --- | --- | --- | --- | --- | --- | --- |
| CBS_11387 | `/tablets/606` | MSL 14 p. 21: De | School | Nippur | 62 | 62 |
| CBS_7072 | `/tablets/595` | MSL 14 p. 20: Ck | School | Nippur | 46 | 46 |
| CBS_7086 | `/tablets/596` | MSL 14 p. 19: Bo, 20: Co | School | Nippur | 42 | 43 |
| N_4030 | `/tablets/599` | MSL 14 p. 19: Cb | School | Nippur | 22 | 22 |
| CBS_7087 | `/tablets/597` | MSL 14 p. 19: Bw | School | Nippur | 17 | 17 |
| N_4949 | `/tablets/600` | MSL 14 p. 19: Bu | School | Nippur | 15 | 15 |
| CBS_15412 | `/tablets/593` | MSL 14 p. 29: Bh | School | Nippur | 14 | 14 |
| BM_96952 | `/tablets/549` | RIME.4.3.6.11 | Monumental | | 8 | 33 |
| BM_113556 | `/tablets/590` | MVAG 35,3 (1935) pp. 105 f. | Letter | Kultepe | 8 | 81 |
| BM_97007 | `/tablets/468` | Jeyes (1989) no. 11 | | Sippar | 7 | 129 |
| N_5087 | `/tablets/601` | MSL 14 p. 19: Bw | School | Nippur | 7 | 7 |
| N_6210 | `/tablets/603` | MSL 14 p. 20: Cu | School | Nippur | 7 | 7 |
| VAT_9652 | `/tablets/572` | Roth (1997) MAPD source F | | Ashur | 6 | 644 |
| BM_131505 | `/tablets/589` | Wiseman (1953) no. 126 | | Alalakh | 6 | 207 |
| N_5243 | `/tablets/602` | MSL 14 p. 19: Bz | School | Nippur | 6 | 6 |
| K_686 | `/tablets/558` | SAA 1, 45 | Letter | Nineveh | 5 | 40 |
| VAT_10001 | `/tablets/573` | Roth (1997) MAL B | | Ashur | 5 | 288 |
| VAT_9629 | `/tablets/574` | Roth (1997) MAPD source A | | Ashur | 5 | 85 |
| N_3996 | `/tablets/598` | MSL 14 p. 19: Bk | School | Nippur | 5 | 5 |
| BM_115110 | `/tablets/591` | MVAG 35,3 (1935) pp. 106 f. | Letter | Kultepe | 4 | 79 |
| BM_97342 | `/tablets/467` | Jeyes (1989) no. 12 | | Sippar | 3 | 51 |
| VAT_9562 | `/tablets/490` | RIMA.0.98.1 | Monumental | Ashur | 3 | 42 |
| 83_1-18_420 | `/tablets/504` | SAA 2, 4 | | Nineveh | 3 | 92 |
| BM_131447 | `/tablets/524` | Wiseman (1953) no. 3 | | Alalakh | 3 | 153 |
| CBS_6923 | `/tablets/594` | MSL 14 p. 20: Cg | School | Nippur | 3 | 3 |
| CBS_2256 | `/tablets/615` | | School | Nippur | 3 | 16 |
| CBS_7130 | `/tablets/640` | Alster (1997) pl.65 | School | Nippur | 3 | 9 |
| UM_41-41-2 | `/tablets/664` | Gwaltney (1983) no. 58 | Letter | Kultepe | 3 | 60 |
| 82_5-22_130 | `/tablets/470` | SAA 2, 9 | | Nineveh | 2 | 208 |
| BM_38120 | `/tablets/502` | MSL 16 p. 73 | School | Babylon | 2 | 580 |
| K_486 | `/tablets/506` | SAA 16, 2 | Letter | Nineveh | 2 | 36 |
| BM_57706 | `/tablets/534` | Bongenaar (1997) pp. 393-394 | Administrative | Sippar | 2 | 21 |
| BM_119045 | `/tablets/539` | RIME.4.2.8.3 | Monumental | Ur | 2 | 8 |
| BM_120524 | `/tablets/571` | RIME.4.2.7.2 | Monumental | Ur | 2 | 16 |
| VAT_9140 | `/tablets/575` | Roth (1997) MAPD source G | | Ashur | 2 | 98 |
| 56_9-9_162 | `/tablets/577` | RIMA.0.78.20 | Monumental | | 2 | 13 |
| BM_87572 | `/tablets/612` | Jeyes (1989) no. 17 | | | 2 | 30 |
| BM_131506 | `/tablets/613` | Wiseman (1953) no. 128 | Administrative | Alalakh | 2 | 76 |
| N_6013 | `/tablets/623` | | School | Nippur | 2 | 22 |
| CBS_15100 | `/tablets/636` | | School | Nippur | 2 | 12 |
| N_5169 | `/tablets/647` | | School | Nippur | 2 | 35 |
| N_5910 | `/tablets/650` | | School | Nippur | 2 | 10 |
| K_39 | `/tablets/483` | MSL 16 p. 117 | School | Nineveh | 1 | 500 |
| VA_Ass_3221_c | `/tablets/491` | RIMA.1.0.60.1 | Monumental | Ashur | 1 | 27 |
| K_15272 | `/tablets/492` | SAA 2, 2 | | Nineveh | 1 | 232 |
| 91_5-9_3 | `/tablets/505` | SAA 16, 17 | Letter | Nineveh | 1 | 58 |
| K_1542 | `/tablets/507` | SAA 16, 1 | Letter | Nineveh | 1 | 96 |
| BM_114342 | `/tablets/540` | RIME.4.2.8.5 | Monumental | Eridu | 1 | 60 |
| VA_8251 | `/tablets/541` | RIMA.0.61.1 | Monumental | Ashur | 1 | 62 |
| BM_116423 | `/tablets/547` | RIME.4.2.14.5 | Monumental | Ur | 1 | 132 |
| K_592 | `/tablets/559` | SAA 1, 5 | Letter | Nineveh | 1 | 14 |
| BM_99332 | `/tablets/563` | RIMA.0.39.2 | Monumental | Nineveh | 1 | 13 |
| Rm2_427 | `/tablets/564` | SAA 2, 1 | | Nineveh | 1 | 100 |
| CBS_6591 | `/tablets/638` | | School | Nippur | 1 | 47 |
| CBS_9847 | `/tablets/643` | | School | Nippur | 1 | 5 |
| N_4577 | `/tablets/644` | | School | Nippur | 1 | 13 |
| N_5384 | `/tablets/648` | | School | Nippur | 1 | 15 |
| N_5458 | `/tablets/649` | | School | Nippur | 1 | 16 |

Answer:

### 19. Are all the signs on BM_130738 Akkadian?

All 800 signs on BM_130738 (`/tablets/523`, Smith (1949)) have the note `lang autoset to akk`: the language was set for the whole tablet. Is Akkadian correct for all of them?

Answer:

## The structure of the data

### 20. Can a tablet have more than one recipient?

Answer:

### 21. Will anyone enter data into these empty fields?

No tablet or record has a value in these fields:

- Tablets: city site, sub-locality, dynasty, function and reign.
- The tables of city sites and sub-localities.
- CDP records: form name and notes.

Answer:

### 22. Can a tablet have a function?

Signs have a function, for example syllable or logogram. The tablet table also has a function field, which is empty.

Answer:

### 23. Are these period dates placeholders?

The periods Archaic, Late Third Millennium and Early Dynastic all have the dates 5000 BC to 5000 BC.

Answer:

### 24. Are the unused years needed?

The data have 2,600 years. Tablets and reigns refer to 320 of them.

Answer:

## Publications

The CDLI values come from the snapshot of the CDLI catalogue. See [Links to catalogues](schema-and-data-questions.md#links-to-catalogues).

### 25. Which numbers are correct?

The publication in the data and the CDLI entry with the same museum number give different volume, page, text or siglum numbers.

| Tablet | Page | Publication | CDLI entry | CDLI publication |
| --- | --- | --- | --- | --- |
| BM_22468 | `/tablets/512` | RIME.3/1.1.7.18 | P232470 | RIME 3/1.01.07.017, ex. 02 |
| BM_87235 | `/tablets/511` | RIME.3/1.1.7.39 | P233922 | RIME 3/1.01.07.038, ex. 01 |
| BM_14030 | `/tablets/542` | UF 10 (1978) 124 no. 5 | P405411 | UF 10, 142 05 |
| BM_14070 | `/tablets/543` | UF 10 (1978) 124 no. 15 | P405421 | UF 10, 147 15 |
| BM_14082 | `/tablets/544` | UF 10 (1978) 124 no. 24 | P405430 | UF 10, 151 24 |
| BM_37857 | `/tablets/629` | MSL 16 p. 74 | P349927 | MSL 16, 075, BM 037857 |
| BM_40127 | `/tablets/472` | MSL 16 p. 49 | P349930 | MSL 16, 345, BM 040127 |
| CBS_15412 | `/tablets/593` | MSL 14 p. 29: Bh | P227844 | MSL 14, 019 Bh |
| CBS_7087 | `/tablets/597` | MSL 14 p. 19: Bw | P229408 | MSL 14, 019 Cf |

The seal impressions BM_14030_seal and BM_14070_seal have the same publications as their tablets. N_5087 (`/tablets/601`) also has `MSL 14 p. 19: Bw`, and CDLI gives Bw for N_5087.

Answer:

### 26. Which publication does each of these tablets have?

These 43 tablets have no publication. The table gives the primary publication and the publication history of the CDLI entry with the same museum number. `unpublished unassigned ?` is the CDLI value for an entry without a publication. CDLI has no entry for BM_40819 and BM_68332.

| Tablet | Page | CDLI entry | CDLI primary publication | CDLI publication history |
| --- | --- | --- | --- | --- |
| BM_40819 | `/tablets/630` | none |  |  |
| BM_68332 | `/tablets/628` | none |  |  |
| CBS_10180 | `/tablets/605` | P265430 | MSL 12, 212 F' |  |
| CBS_10365 | `/tablets/632` | P230213 | unpublished unassigned ? |  |
| CBS_12515 | `/tablets/633` | P227685 | MSL 12, 032 U'' | OIP 011, p.16 (unpub. dup.); Veldhuis EEN 297 |
| CBS_13667 | `/tablets/634` | P230617 | Farmer's Instructions p.173. |  |
| CBS_14108 | `/tablets/635` | P227768 | PBS 11/3, 068 | MSL 12, 030 C' |
| CBS_15100 | `/tablets/636` | P227804 | MSL 14, 022 Es |  |
| CBS_2256 | `/tablets/615` | P227890 | OIP 011, 005 (CBS 02256) | MSL 12, 030 B', 192 X, 10, 199 |
| CBS_4812 | `/tablets/637` | P227961 | OIP 011, p. 014, CBS 04812 + | Civil Farmer's Instructions p.173; Veldhuis EEN 311; MSL 09, 051 S06, CBS 06755 |
| CBS_4819 | `/tablets/666` | P227968 | OIP 011, 114 | MSL 12, 030 L' |
| CBS_6591 | `/tablets/638` | P227953 | OIP 011, 105 + 109 + 148 | MSL 12, 029 L + 031 Y'; MSL 05, 169 (on OIP 011, 148). |
| CBS_6972 | `/tablets/616` | P229096 | OIP 011, 253 | MSL 8/1 (V14) rev. only. |
| CBS_7074 | `/tablets/639` | P229436 | PBS 12, 56 | MSL 12, 030 M'; MSL 14, 22 Eo |
| CBS_7877 | `/tablets/641` | P250418 | unpublished unassigned ? |  |
| CBS_7993 | `/tablets/642` | P231711 | unpublished unassigned ? |  |
| CBS_8066 | `/tablets/617` | P229421 | MSL 14, 020 Cx, CBS 08066 | MSL 12, 030 G' |
| CBS_8298 | `/tablets/618` | P230006 | OIP 011, 137 | Veldhuis EEN 311 |
| CBS_9847 | `/tablets/643` | P228068 | EEN 297, CBS 09847+ | OIP 011, p.16 (unpub. dup.) |
| K_4600 | `/tablets/477` | P385978 | CT 19, pl. 39, K 04600 |  |
| N_4577 | `/tablets/644` | P228281 | unpublished unassigned ? |  |
| N_4909 | `/tablets/645` | P231175 | CDLI Literary 000821, ex. 034 | Veldhuis, Niek, JAOS 120 (2000) 399 |
| N_5044 | `/tablets/619` | P231241 | unpublished unassigned ? | Peterson, ZA 101, 261 |
| N_5047 | `/tablets/646` | P231244 | unpublished unassigned ? |  |
| N_5129 | `/tablets/620` | P229543 | MSL 12, 032 + MSL 13, 013 J, 014 R, C1 |  |
| N_5169 | `/tablets/647` | P228396 | MSL 12, 030 S' |  |
| N_5384 | `/tablets/648` | P228454 | unpublished unassigned ? |  |
| N_5458 | `/tablets/649` | P228471 | MSL 12, 031 P'' | MSL 13, 065 F1 (pub as 5448) |
| N_5553 | `/tablets/621` | P228494 | MSL 11, 094 Y |  |
| N_5910 | `/tablets/650` | P229535 | MSL 12, 031 F'' |  |
| N_5914 | `/tablets/622` | P230947 | unpublished unassigned ? |  |
| N_6006 | `/tablets/651` | P230059 | EEN 315, N 6006 |  |
| N_6013 | `/tablets/623` | P229543 | MSL 12, 032 + MSL 13, 013 J, 014 R, C1 |  |
| N_6228 | `/tablets/658` | P229389 | MSL 14, 018 Ao |  |
| Rm2_25 | `/tablets/482` | P386427 | CT 12, pl. 39, Rm 2, 025 |  |
| UM_29_15_513 | `/tablets/654` | P228646 | MSL 12, 032 Z'' |  |
| UM_29_15_888 | `/tablets/624` | P228687 | MSL 12, 031 H'' | MSL 14, p. 21 Dj |
| UM_29_15_938 | `/tablets/653` | P228689 | MSL 12, 031 Q'' |  |
| UM_29_15_939 | `/tablets/655` | P228690 | MSL 14, 022 Eg |  |
| UM_29_15_964 | `/tablets/625` | P228692 | MSL 12, 030 D' |  |
| UM_29_16_610 | `/tablets/659` | P228789 | MSL 12, 029 M |  |
| UM_55_21_392 | `/tablets/656` | P228927 | unpublished unassigned ? |  |
| UM_55_21_418 | `/tablets/657` | P228859 | MSL 12, 031 C'' |  |

Answer:

### 27. What are the museum numbers of these tablets?

No CDLI entry has these numbers. UET 6/3 is a volume of texts, not a collection.

| Tablet | Page | Publication |
| --- | --- | --- |
| UET_6/3_378 | `/tablets/608` | Alster (1997) p. 328 |
| UET_6/3_452 | `/tablets/607` | Alster (1997) p. 328 |
| W_18202_25 | `/tablets/662` | AUWE 5, 129 |
| Wx17 | `/tablets/535` | AUWE 5, 68 |

Answer:

## Comparison with CDLI

`cdpp check-cdli` writes the tables of these questions from the snapshot of the CDLI catalogue of August 2022. Run it again after changes to the data. A CDLI value that ends with `?` is uncertain in CDLI. A tablet agrees if one of its CDLI entries agrees. The tables do not include a tablet if its CDLI entries give no value.

### 28. Which period is correct?

The period in the data does not agree with the period of the CDLI entry with the same museum number. Is the first table correct? For each tablet in the second table, which period is correct?

<!-- cdpp check-cdli: period -->

These CDLI periods agree with these periods in the data:

| CDLI period | Period | Sub-periods |
| --- | --- | --- |
| Uruk IV | Archaic | all |
| Uruk III | Archaic | all |
| ED I-II | Early Dynastic | ED I, or none |
| ED IIIa | Early Dynastic | ED IIIa, or none |
| ED IIIb | Early Dynastic | ED IIIb, or none |
| Old Akkadian | Late Third Millennium | Old Akkadian, or none |
| Lagash II | Late Third Millennium | Lagash II, or none |
| Ur III | Late Third Millennium | Ur III, or none |
| Early Old Babylonian | Old Babylonian | Early Old Babylonian, or none |
| Old Babylonian | Old Babylonian | Late Old Babylonian, or none |
| Old Assyrian | Old Assyrian | all |
| Middle Babylonian | Middle Babylonian | all |
| Middle Assyrian | Middle Assyrian | all |
| Neo-Assyrian | Neo-Assyrian | all |
| Early Neo-Babylonian | Neo-Babylonian | Early Neo-Babylonian, or none |
| Neo-Babylonian | Neo-Babylonian | Chaldean, or none |
| Achaemenid | Late Babylonian | Achaemenid, or none |
| Hellenistic | Late Babylonian | Greek, or none |

The period in the data does not agree with CDLI:

| Tablet | Page | Period | Sub-period | CDLI entry | CDLI period |
| --- | --- | --- | --- | --- | --- |
| BM_55872 | `/tablets/500` | Late Babylonian | Achaemenid | P367241 | Neo-Babylonian (ca. 626-539 BC) |
| BM_56728 | `/tablets/503` | Late Babylonian | Achaemenid | P314423 | Neo-Babylonian (ca. 626-539 BC) |
| BM_74378 | `/tablets/501` | Late Babylonian | Achaemenid | P365710 | Neo-Babylonian (ca. 626-539 BC) |
| BM_22468 | `/tablets/512` | Late Third Millennium | Ur III | P232470 | Lagash II (ca. 2200-2100 BC) |
| BM_87235 | `/tablets/511` | Late Third Millennium | Ur III | P233922 | Lagash II (ca. 2200-2100 BC) |
| BM_130738 | `/tablets/523` | Middle Assyrian |  | P500443 | Middle Babylonian (ca. 1400-1100 BC) |
| VA_8251 | `/tablets/541` | Middle Assyrian |  | P465507 | Old Babylonian (ca. 1900-1600 BC) |
| VA_Ass_3221_c | `/tablets/491` | Middle Assyrian |  | P465880 | Old Babylonian (ca. 1900-1600 BC) |
| VAT_9562 | `/tablets/490` | Neo-Assyrian | Early Neo-Assyrian | P467535 | Middle Assyrian (ca. 1400-1000 BC) |
| BM_40127 | `/tablets/472` | Neo-Babylonian | Early Neo-Babylonian | P349930 | Neo-Babylonian (ca. 626-539 BC) |
| BM_14030 | `/tablets/542` | Old Babylonian | Early Old Babylonian | P405411 | Old Babylonian (ca. 1900-1600 BC) |
| BM_14030_seal | `/tablets/545` | Old Babylonian | Early Old Babylonian | P405411 | Old Babylonian (ca. 1900-1600 BC) |
| BM_14070 | `/tablets/543` | Old Babylonian | Early Old Babylonian | P405421 | Old Babylonian (ca. 1900-1600 BC) |
| BM_14070_seal | `/tablets/546` | Old Babylonian | Early Old Babylonian | P405421 | Old Babylonian (ca. 1900-1600 BC) |
| BM_14082 | `/tablets/544` | Old Babylonian | Early Old Babylonian | P405430 | Old Babylonian (ca. 1900-1600 BC) |
| BM_80128_seal | `/tablets/548` | Old Babylonian | Early Old Babylonian | P366217 | Old Babylonian (ca. 1900-1600 BC) |
| CBS_10180 | `/tablets/605` | Old Babylonian | Late Old Babylonian | P265430 | Early Old Babylonian (ca. 2000-1900 BC) |
| CBS_11387 | `/tablets/606` | Old Babylonian | Late Old Babylonian | P227671 | Ur III (ca. 2100-2000 BC) ? |
| CBS_14108 | `/tablets/635` | Old Babylonian | Late Old Babylonian | P227768 | Early Old Babylonian (ca. 2000-1900 BC) |
| CBS_15412 | `/tablets/593` | Old Babylonian | Late Old Babylonian | P227844 | Early Old Babylonian (ca. 2000-1900 BC) |
| CBS_4819 | `/tablets/666` | Old Babylonian | Late Old Babylonian | P227968 | Early Old Babylonian (ca. 2000-1900 BC) |

<!-- cdpp check-cdli: end -->

Answer:

### 29. Which city is correct?

The city in the data does not agree with the provenience of the CDLI entry, or the data give no city. Is the first table correct? For each tablet in the other tables, which city is correct?

<!-- cdpp check-cdli: city -->

A city agrees with a CDLI place of the same ancient or modern name, with or without diacritics. These cities also agree with other names:

| City | CDLI names |
| --- | --- |
| Ashur | Assur |
| Drehem | Puzriš-Dagan |
| Eshnunna | Ešnunna |
| Kultepe | Kanesh |
| Sippar | Sippar-Amnanum, Sippar-Yahrurum |

The city in the data does not agree with CDLI:

| Tablet | Page | City | CDLI entry | CDLI provenience |
| --- | --- | --- | --- | --- |
| 91_5-9_3 | `/tablets/505` | Nineveh | P334819 | Sippar-Yahrurum (mod. Tell Abu Habbah) |

The data give no city, and CDLI gives a place:

| Tablet | Page | CDLI entry | CDLI provenience |
| --- | --- | --- | --- |
| VAT_9653 | `/tablets/453` | P466008 | Assur (mod. Qalat Sherqat) |
| 56_9-9_162 | `/tablets/577` | P466444 | Assur (mod. Qalat Sherqat) ? |
| A_1429-1982 | `/tablets/522` | P105441 | Girsu (mod. Tello) |
| BM_87572 | `/tablets/612` | P511846 | Sippar-Yahrurum (mod. Tell Abu Habbah) |
| BM_80161_seal | `/tablets/456` | P285732 | Sippar-Yahrurum (mod. Tell Abu Habbah) ? |
| BM_81388 | `/tablets/554` | P523779 | Sippar-Yahrurum (mod. Tell Abu Habbah) ? |
| BM_81552 | `/tablets/555` | P523778 | Sippar-Yahrurum (mod. Tell Abu Habbah) ? |
| BM_81562 | `/tablets/551` | P523777 | Sippar-Yahrurum (mod. Tell Abu Habbah) ? |
| BM_81596 | `/tablets/552` | P523775 | Sippar-Yahrurum (mod. Tell Abu Habbah) ? |
| BM_91082 | `/tablets/569` | P429914 | Sippar-Yahrurum (mod. Tell Abu Habbah) ? |
| BM_91149 | `/tablets/587` | P431706 | Ur (mod. Tell Muqayyar) |

<!-- cdpp check-cdli: end -->

Answer:

### 30. Which object type or medium is correct?

The object type or the medium in the data does not agree with the CDLI entry. Is the first table correct? For each tablet in the second table, which object type and medium are correct?

<!-- cdpp check-cdli: object -->

An object type agrees with the CDLI object type of the same name. These object types also agree with other CDLI object types:

| Object type | CDLI object types |
| --- | --- |
| cylinder seal | seal (not impression) |
| envelope | envelope, tablet & envelope |
| tablet | tablet, tablet & envelope |

A medium agrees with the first CDLI material: stone agrees with `stone: diorite`. The comparison does not use the CDLI object type `other (see object remarks)`.

The object type or the medium in the data does not agree with CDLI:

| Tablet | Page | Object type | Medium | CDLI entry | CDLI object type | CDLI material |
| --- | --- | --- | --- | --- | --- | --- |
| BM_122669 | `/tablets/561` | architectural feature | clay | P422442 | cone | clay |
| BM_123455 | `/tablets/562` | architectural feature | clay | P422534 | cone | clay |
| Sm_2115 | `/tablets/560` | architectural feature | clay | P466283 | cone | clay |
| BM_80128_seal | `/tablets/548` | envelope | clay | P366217 | tablet | clay |
| BM_121148 | `/tablets/495` | stela | stone | P465958 | prism | clay |
| BM_113207 | `/tablets/469` | tablet | stone | P345489 | tablet | clay |
| 56_9-9_195 | `/tablets/452` | vessel | clay | P466114 | cone | clay |

<!-- cdpp check-cdli: end -->

Answer:

### 31. Which language is correct?

The data give a language to each sign. CDLI gives the languages of each text. The signs and the CDLI entry have no language in common, or some signs have no language, as in [question 18](#18-do-these-signs-have-no-language-or-is-the-language-missing). For each tablet, which language is correct?

<!-- cdpp check-cdli: language -->

The languages of the signs in the data and the CDLI languages have no language in common:

| Tablet | Page | Languages | CDLI entry | CDLI language |
| --- | --- | --- | --- | --- |
| K_5422_a | `/tablets/480` | Sumerian | P345979 | Akkadian |

Some signs have no language, and CDLI gives a language:

| Tablet | Page | Without language | All | Languages of the other signs | CDLI entry | CDLI language |
| --- | --- | --- | --- | --- | --- | --- |
| CBS_11387 | `/tablets/606` | 62 | 62 |  | P227671 | Sumerian |
| CBS_7072 | `/tablets/595` | 46 | 46 |  | P229413 | Sumerian |
| CBS_7086 | `/tablets/596` | 42 | 43 | Sumerian | P229400 | Sumerian |
| N_4030 | `/tablets/599` | 22 | 22 |  | P228220 | Sumerian |
| CBS_7087 | `/tablets/597` | 17 | 17 |  | P229408 | Sumerian |
| N_4949 | `/tablets/600` | 15 | 15 |  | P231195 | Sumerian |
| CBS_15412 | `/tablets/593` | 14 | 14 |  | P227844 | Sumerian |
| BM_96952 | `/tablets/549` | 8 | 33 | Sumerian | P431849 | Sumerian |
| BM_97007 | `/tablets/468` | 7 | 129 | Akkadian | P511840 | Akkadian |
| N_5087 | `/tablets/601` | 7 | 7 |  | P229307 | Sumerian |
| N_6210 | `/tablets/603` | 7 | 7 |  | P229419 | Sumerian |
| BM_131505 | `/tablets/589` | 6 | 207 | Akkadian | P348093 | Akkadian |
| N_5243 | `/tablets/602` | 6 | 6 |  | P228424 | Sumerian |
| K_686 | `/tablets/558` | 5 | 40 | Akkadian | P334118 | Akkadian |
| N_3996 | `/tablets/598` | 5 | 5 |  | P228202 | Sumerian |
| 83_1-18_420 | `/tablets/504` | 3 | 92 | Akkadian | P314346 | Akkadian |
| BM_131447 | `/tablets/524` | 3 | 153 | Akkadian | P452243 | Akkadian |
| BM_97342 | `/tablets/467` | 3 | 51 | Akkadian | P511841 | Akkadian |
| CBS_2256 | `/tablets/615` | 3 | 16 | Sumerian | P227890 | Sumerian |
| CBS_6923 | `/tablets/594` | 3 | 3 |  | P229367 | Sumerian |
| CBS_7130 | `/tablets/640` | 3 | 9 | Sumerian | P229739 | Sumerian |
| UM_41-41-2 | `/tablets/664` | 3 | 60 | Akkadian | P361171 | Akkadian |
| VAT_9562 | `/tablets/490` | 3 | 42 | Akkadian | P467535 | Akkadian |
| 56_9-9_162 | `/tablets/577` | 2 | 13 | Akkadian | P466444 | Akkadian |
| 82_5-22_130 | `/tablets/470` | 2 | 208 | Akkadian | P237185 | Akkadian |
| BM_87572 | `/tablets/612` | 2 | 30 | Akkadian | P511846 | Akkadian |
| CBS_15100 | `/tablets/636` | 2 | 12 | Sumerian | P227804 | Sumerian |
| K_486 | `/tablets/506` | 2 | 36 | Akkadian | P334192 | Akkadian |
| N_5169 | `/tablets/647` | 2 | 35 | Sumerian | P228396 | Sumerian |
| N_5910 | `/tablets/650` | 2 | 10 | Sumerian | P229535 | Sumerian |
| N_6013 | `/tablets/623` | 2 | 22 | Sumerian | P229543 | Sumerian |
| 91_5-9_3 | `/tablets/505` | 1 | 58 | Akkadian | P334819 | Akkadian |
| BM_99332 | `/tablets/563` | 1 | 13 | Akkadian | P465798 | Akkadian |
| CBS_9847 | `/tablets/643` | 1 | 5 | Sumerian | P228068 | Sumerian |
| K_15272 | `/tablets/492` | 1 | 232 | Akkadian | P336039 | Akkadian |
| K_1542 | `/tablets/507` | 1 | 96 | Akkadian | P334624 | Akkadian |
| K_592 | `/tablets/559` | 1 | 14 | Akkadian | P334194 | Akkadian |
| N_4577 | `/tablets/644` | 1 | 13 | Sumerian | P228281 | Sumerian |
| Rm2_427 | `/tablets/564` | 1 | 100 | Akkadian | P240211 | Akkadian |
| VA_8251 | `/tablets/541` | 1 | 62 | Akkadian | P465507 | Akkadian |
| VA_Ass_3221_c | `/tablets/491` | 1 | 27 | Akkadian | P465880 | Akkadian |

<!-- cdpp check-cdli: end -->

Answer:
