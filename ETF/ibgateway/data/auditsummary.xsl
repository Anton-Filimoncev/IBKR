<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
	<!-- Audit Trail Convertion Stylesheet @Date: 12/19/03 @Author: Ahmet Bozkurt -->
	<xsl:template match="/">
		<html>
			<head>
				<title>Summary Audit Trail</title>
			</head>
			<body>
				<table border="1" cellpading="0" cellspacing="0">
					<tr>
						<th bgcolor="#CCCCCC">Action</th>
						<th bgcolor="#CCCCCC">Time</th>
						<th nowrap="nowrap" bgcolor="#CCCCCC">Client Order Id</th>
						<th nowrap="nowrap" bgcolor="#CCCCCC">Order Id</th>
						<th bgcolor="#CCCCCC">Side</th>
						<th bgcolor="#CCCCCC">Size</th>
						<th bgcolor="#CCCCCC">Contract</th>
						<th nowrap="nowrap" bgcolor="#CCCCCC">Order Type</th>
						<th bgcolor="#CCCCCC">Price</th>
						<th bgcolor="#CCCCCC">TIF</th>
						<th bgcolor="#CCCCCC">Misc</th>
					</tr>
					<xsl:apply-templates/>
				</table>
			</body>
		</html>
	</xsl:template>
	<xsl:template match="Entry">
		<tr>
			<td nowrap="nowrap">
				<strong>
					<xsl:value-of select="@type"/>
				</strong>
			</td>
			<td nowrap="nowrap">
				<xsl:choose>
					<xsl:when test="field[@tag = '52']">                                                     <!-- Time -->
						<xsl:value-of select="field[@tag = '52']/@val"/>
					</xsl:when>
					<xsl:otherwise>
						-
					</xsl:otherwise>
				</xsl:choose>
			</td>
			<td nowrap="nowrap">
				<xsl:choose>
					<xsl:when test="field[@tag = '11']">                                                     <!-- Client Order ID -->
						<xsl:value-of select="field[@tag = '11']/@val"/>
					</xsl:when>
					<xsl:otherwise>
				     	-
				    </xsl:otherwise>
				</xsl:choose>
			</td>
			<td nowrap="nowrap">
				<xsl:choose>
					<xsl:when test="field[@tag = '37']">                                                     <!-- Order ID -->
						<xsl:value-of select="field[@tag = '37']/@val"/>
					</xsl:when>
					<xsl:otherwise>
				     	-
				    </xsl:otherwise>
				</xsl:choose>
			</td>
			<td nowrap="nowrap">
				<xsl:choose>
					<xsl:when test="field[@tag = '54']">                                                  <!-- Side -->
						<xsl:choose>
							<xsl:when test="field[@tag = '54']/@val='1'">
								Buy
							</xsl:when>
							<xsl:when test="field[@tag = '54']/@val='2'">
								Sell
							</xsl:when>
							<xsl:when test="field[@tag = '54']/@val='3'">
								BuyMinus
							</xsl:when>
							<xsl:when test="field[@tag = '54']/@val='4'">
								SellPlus
							</xsl:when>
							<xsl:when test="field[@tag = '54']/@val='5'">
								SellShort
							</xsl:when>
							<xsl:otherwise>
								<xsl:value-of select="field[@tag = '54']/@val"/>
							</xsl:otherwise>
						</xsl:choose>
					</xsl:when>
					<xsl:otherwise>
							-
					</xsl:otherwise>
				</xsl:choose>
			</td>
			<td nowrap="nowrap">
			<xsl:choose>   
			<xsl:when test="@type!='Filled' and @type!='PartiallyFilled'">
				<xsl:choose>
					<xsl:when test="field[@tag = '38']">                                                    <!-- Size -->
						<xsl:value-of select="field[@tag = '38']/@val"/>
					</xsl:when>
					<xsl:otherwise>
				 		-
				 </xsl:otherwise>
				</xsl:choose>
			</xsl:when>
			<xsl:when test="@type='Filled' or @type='PartiallyFilled'">
				<xsl:choose>
					<xsl:when test="field[@tag = '32']">                                                    <!-- LastShares -->
						<xsl:value-of select="field[@tag = '32']/@val"/>
					</xsl:when>
					<xsl:otherwise>
				 		-
				 </xsl:otherwise>
				</xsl:choose>			
			</xsl:when>
			<xsl:otherwise>
				 	-
			</xsl:otherwise>
			</xsl:choose>
			</td>
			<td nowrap="nowrap">
				<xsl:choose>                                                                                        <!--Contrract Info -->
					<xsl:when test="field[@tag = '167']">                                                 <!-- Security Type -->
						<xsl:choose>
							<xsl:when test="field[@tag='167']/@val='CS' or field[@tag='167']/@val='PS'">
								<xsl:value-of select="field[@tag = '55']/@val"/>                    <!-- Symbol -->
							</xsl:when>
							<xsl:when test="field[@tag='167']/@val='FUT'">
								<xsl:value-of select="field[@tag = '55']/@val"/> - <xsl:value-of select="field[@tag = '200']/@val"/>
							</xsl:when>
							<xsl:otherwise>
								<xsl:value-of select="field[@tag = '55']/@val"/> -
							<xsl:value-of select="field[@tag = '200']/@val"/> -       <!--Expiry-->
							<xsl:value-of select="field[@tag = '202']/@val"/> -	     <!--= Strike-->
							<xsl:choose>
								<xsl:when test="field[@tag = '201']/@val='0'">			 <!--P/C-->
									P
								</xsl:when>
								<xsl:when test="field[@tag = '201']/@val='1'">
									C
								</xsl:when>
								<xsl:otherwise>
									<xsl:value-of select="@val"/>
								</xsl:otherwise>
							</xsl:choose>
							</xsl:otherwise>
						</xsl:choose>
					</xsl:when>
					<xsl:otherwise>
				 		-
				 </xsl:otherwise>
				</xsl:choose>
			</td>
			<td nowrap="nowrap">
				<xsl:choose>
					<xsl:when test="field[@tag = '40']">                                             <!-- Order Type -->
						<xsl:choose>
							<xsl:when test="field[@tag = '40']/@val='0'">
							None
						</xsl:when>
							<xsl:when test="field[@tag = '40']/@val='1'">
							Market
						</xsl:when>
							<xsl:when test="field[@tag = '40']/@val='2'">
							Limit
						</xsl:when>
							<xsl:when test="field[@tag = '40']/@val='3'">
							Stop
						</xsl:when>
							<xsl:when test="field[@tag = '40']/@val='4'">
							StopLimit
						</xsl:when>
							<xsl:when test="field[@tag = '40']/@val='5'">
							MOC
						</xsl:when>
							<xsl:when test="field[@tag = '40']/@val='6'">
							WithOrWithout
						</xsl:when>
							<xsl:when test="field[@tag = '40']/@val='7'">
							LimitOrBetter
						</xsl:when>
							<xsl:when test="field[@tag = '40']/@val='8'">
							LimitWithOrWithout
						</xsl:when>
							<xsl:when test="field[@tag = '40']/@val='9'">
							OnBasis
						</xsl:when>
							<xsl:when test="field[@tag = '40']/@val='A'">
							OnClose
						</xsl:when>
							<xsl:when test="field[@tag = '40']/@val='B'">
							LOC
						</xsl:when>
							<xsl:when test="field[@tag = '40']/@val='C'">
							ForexMarket
						</xsl:when>
							<xsl:when test="field[@tag = '40']/@val='D'">
							PreviouslyQuoted
						</xsl:when>
							<xsl:when test="field[@tag = '40']/@val='E'">
							Relative
						</xsl:when>
							<xsl:when test="field[@tag = '40']/@val='F'">
							RelativeToStock
						</xsl:when>
							<xsl:when test="field[@tag = '40']/@val='G'">
							ForexSwap
						</xsl:when>
							<xsl:when test="field[@tag = '40']/@val='H'">
							ForexPreviouslyQuoted
						</xsl:when>
							<xsl:when test="field[@tag = '40']/@val='I'">
							Funari
						</xsl:when>
							<xsl:when test="field[@tag = '40']/@val='K'">
							Market2Limit
						</xsl:when>
							<xsl:when test="field[@tag = '40']/@val='Q'">
							QuoteRequest
						</xsl:when>
							<xsl:when test="field[@tag = '40']/@val='T'">
							TrailingStop
						</xsl:when>
							<xsl:when test="field[@tag = '40']/@val='P'">
							Pegged
						</xsl:when>
							<xsl:when test="field[@tag = '40']/@val=' '">
								-
						</xsl:when>
							<xsl:otherwise>
								<xsl:value-of select="field[@tag = '40']/@val"/>
							</xsl:otherwise>
						</xsl:choose>
					</xsl:when>
					<xsl:otherwise>
						-
					</xsl:otherwise>
				</xsl:choose>
			</td>
			<td nowrap="nowrap">
			<xsl:choose>
				<xsl:when  test="@type!='Filled'">
				<xsl:choose>
					<xsl:when test="field[@tag = '44']">                                                    <!-- Limit Price -->
						<xsl:value-of select="field[@tag = '44']/@val"/>
					</xsl:when>
					<xsl:otherwise>
				 		-
				 </xsl:otherwise>
				</xsl:choose>
				</xsl:when>
				<xsl:when test="@type='Filled'">
				<xsl:choose>
					<xsl:when test="field[@tag = '31']">                                                    <!-- LastPx -->
						<xsl:value-of select="field[@tag = '31']/@val"/>
					</xsl:when>
					<xsl:otherwise>
				 		-
				 </xsl:otherwise>
				</xsl:choose>			
				</xsl:when>
				<xsl:otherwise>
					-
				</xsl:otherwise>
			</xsl:choose>
			</td>			
			<td nowrap="nowrap">
				<xsl:choose>
					<xsl:when test="field[@tag = '59']">                                   <!--TIF-->
						<xsl:choose>
							<xsl:when test="field[@tag = '59']/@val='0'">
						DAY
					</xsl:when>
							<xsl:when test="field[@tag = '59']/@val='1'">
						GTC
					</xsl:when>
							<xsl:when test="field[@tag = '59']/@val='2'">
						OPG
					</xsl:when>
							<xsl:when test="field[@tag = '59']/@val='3'">
						IOC
					</xsl:when>
							<xsl:when test="field[@tag = '59']/@val='4'">
						FOK
					</xsl:when>
							<xsl:when test="field[@tag = '59']/@val='5'">
						GTX
					</xsl:when>
							<xsl:when test="field[@tag = '59']/@val='6'">
						GTD
					</xsl:when>
							<xsl:when test="field[@tag = '59']/@val='7'">
						CLG
					</xsl:when>
							<xsl:when test="field[@tag = '59']/@val='8'">
						AUC
					</xsl:when>
							<xsl:when test="field[@tag = '59']/@val=' '">
								-
					</xsl:when>
							<xsl:otherwise>
								<xsl:value-of select="field[@tag = '59']/@val"/>
							</xsl:otherwise>
						</xsl:choose>
					</xsl:when>
					<xsl:otherwise>
						-
			</xsl:otherwise>
				</xsl:choose>
			</td>
			<td nowrap="nowrap">
			<xsl:for-each select="field">
			<xsl:choose>
				<xsl:when test="@tag='35'">
				</xsl:when>
				<xsl:when test="@tag='7'">
					BeginSeqNo=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='15'">
					Currency=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='16'">
					EndSeqNo=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='17'">
					ExecID=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='30'">
					LastMarket=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='57'">
					TargetSubID=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='50'">
					SenderSubID=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='34'">
				</xsl:when>
				<xsl:when test="@tag='97'">
					PossResend=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='122'">
				</xsl:when>
				<xsl:when test="@tag='10'">
				</xsl:when>
				<xsl:when test="@tag='98'">
					EncryptMethod=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='108'">
					HeartBtInt=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='58'">
					Text=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='45'">
					RefSeqNo=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='123'">
					GapFillFlag=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='36'">
					NewSeqNum=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='112'">
					TestReqID=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='102'">
					CxlRejReason=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='20'">
					ExecTransType=
					<xsl:choose>
						<xsl:when test="@val='0'">
							New;
						</xsl:when>
						<xsl:when test="@val='1'">
							Cancel;
						</xsl:when>
						<xsl:when test="@val='2'">
							Correct;
						</xsl:when>
						<xsl:when test="@val='3'">
							Status;
						</xsl:when>
						<xsl:when test="@val='z'">
							SplitBust;
						</xsl:when>
						<xsl:otherwise>
							<xsl:value-of select="@val"/>;
						</xsl:otherwise>
					</xsl:choose>	
				</xsl:when>

				<xsl:when test="@tag='19'">
					ExecRefID=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='39'">
					OrdStatus=
					<xsl:choose>
					<xsl:when test="@val='0'">
						New;
					</xsl:when>
					<xsl:when test="@val='1'">
						PartiallyFilled;
					</xsl:when>
					<xsl:when test="@val='2'">
						Filled;
					</xsl:when>
					<xsl:when test="@val='3'">
						DoneForTheDay;
					</xsl:when>
					<xsl:when test="@val='4'">
						Canceled;
					</xsl:when>
					<xsl:when test="@val='5'">
						Replaced;
					</xsl:when>
					<xsl:when test="@val='6'">
						PendingCancelReplace;
					</xsl:when>
					<xsl:when test="@val='7'">
						Stopped;
					</xsl:when>
					<xsl:when test="@val='8'">
						Rejected;
					</xsl:when>
					<xsl:when test="@val='9'">
						Suspended;
					</xsl:when>
					<xsl:when test="@val='A'">
						PendingNew;
					</xsl:when>
					<xsl:when test="@val='B'">
						Calculated;
					</xsl:when>
					<xsl:when test="@val='C'">
						Expired;
					</xsl:when>
					<xsl:when test="@val='D'">
						PendingCancel;
					</xsl:when>
					<xsl:otherwise>
						<xsl:value-of select="@val"/>;
					</xsl:otherwise>
					</xsl:choose>	
				</xsl:when>
				<xsl:when test="@tag='14'">
					CumQty=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='6'">
					AvgPx=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='60'">
					TransactTime=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='99'">
					AuxPrice=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='47'">
					Rule80A=
					<xsl:choose>
					<xsl:when test="@val='A'">
						AgenySingleOrder;
					</xsl:when>
					<xsl:when test="@val='Y'">
						ProgramOrder;
					</xsl:when>
					<xsl:otherwise>
							<xsl:value-of select="@val"/>;
					</xsl:otherwise>
					</xsl:choose>
				</xsl:when>	
				<xsl:when test="@tag='77'">
						OpenClose=
						<xsl:choose>
						<xsl:when test="@val='O'">
							Open;
						</xsl:when>
						<xsl:when test="@val='C'">
							Close;
						</xsl:when>
						<xsl:otherwise>
							<xsl:value-of select="@val"/>;
						</xsl:otherwise>
						</xsl:choose>
				</xsl:when>
				<xsl:when test="@tag='103'">
					OrdRejReason=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='41'">
					OrigClOrdID=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='125'">
					CxlType=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='48'">
					SecurityID=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='141'">
					ResetSeqNumFlag=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='207'">
					SecurityExchange=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='167'">
					SecurityType=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='205'">
					MaturityDay=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='202'">
					StrikePrice=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='204'">
					CustomerOrFirm=
					<xsl:choose>
					<xsl:when test="@val='0'">
						Customer;
					</xsl:when>
					<xsl:when test="@val='1'">
						Firm;
					</xsl:when>
					<xsl:otherwise>
						<xsl:value-of select="@val"/>;
					</xsl:otherwise>
					</xsl:choose>
				</xsl:when>
				<xsl:when test="@tag='96'">
					RawData=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='95'">
					RawDataLength=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='1'">
					Account=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='81'">
					ProcessCode=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='18'">
					ExecInst=
					<xsl:choose>
					<xsl:when test="@val='1'">
						Notheld;
					</xsl:when>
					<xsl:when test="@val='2'">
						Work;
					</xsl:when>
					<xsl:when test="@val='3'">
						Goalong;
					</xsl:when>
					<xsl:when test="@val='4'">
						OverTheDay;
					</xsl:when>
					<xsl:when test="@val='5'">
						Held;
					</xsl:when>
					<xsl:when test="@val='6'">
						ParticipateDontInitiate;
					</xsl:when>
					<xsl:when test="@val='7'">
						Strictscale;
					</xsl:when>
					<xsl:when test="@val='8'">
						TryToScale;
					</xsl:when>
					<xsl:when test="@val='9'">
						StayOnBidside;
					</xsl:when>
					<xsl:when test="@val='0'">
						StayOnOfferside;
					</xsl:when>
					<xsl:when test="@val='A'">
						Nocross;
					</xsl:when>
					<xsl:when test="@val='B'">
						OKToCross;
					</xsl:when>
					<xsl:when test="@val='C'">
						CallFirst;
					</xsl:when>
					<xsl:when test="@val='D'">
						PercentOfVolume;
					</xsl:when>
					<xsl:when test="@val='E'">
						DNI;
					</xsl:when>
					<xsl:when test="@val='F'">
						DNR;
					</xsl:when>
					<xsl:when test="@val='G'">
						AON;
					</xsl:when>
					<xsl:when test="@val='I'">
						InstitutionsOnly;
					</xsl:when>
					<xsl:when test="@val='L'">
						LastPeg;
					</xsl:when>
					<xsl:when test="@val='M'">
						MidPricePeg;
					</xsl:when>
					<xsl:when test="@val='N'">
						NonNegotiable;
					</xsl:when>
					<xsl:when test="@val='O'">
						OpeningPeg;
					</xsl:when>
					<xsl:when test="@val='P'">
						MarketPeg;
					</xsl:when>
					<xsl:when test="@val='R'">
						PrimaryPeg;
					</xsl:when>
					<xsl:when test="@val='S'">
						Suspend;
					</xsl:when>
					<xsl:when test="@val='U'">
						CustomerDisplayInstruction;
					</xsl:when>
					<xsl:when test="@val='V'">
						Netting;
					</xsl:when>
					<xsl:when test="@val='W'">
						PegToVWAP;
					</xsl:when>
					<xsl:when test="@val='X'">
						TradeAlong;
					</xsl:when>
					<xsl:when test="@val='Y'">
						TryToStop;
					</xsl:when>
					<xsl:when test="@val='Z'">
						CancelIfNotBest;
					</xsl:when>
					<xsl:when test="@val='a'">
						TrailingStop;
					</xsl:when>
					<xsl:when test="@val='e'">
						Algo;
					</xsl:when>
					<xsl:when test="@val='s'">
						PegToStk;
					</xsl:when>
					<xsl:otherwise>
						<xsl:value-of select="@val"/>;
					</xsl:otherwise>
					</xsl:choose>
				</xsl:when>
				<xsl:when test="@tag='100'">
					ExDestination=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='5006'">
					SessionNo=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='5030'">
					Shared=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='21'">
					HandlInst=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='9131'">
					PriceCheck=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='9130'">
					OrdAction=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='9306'">
					OrigOrderDate=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='211'">
					PegDifference=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='150'">
					ExecType=
					<xsl:choose>
					<xsl:when test="@val='0'">
						New;
					</xsl:when>
					<xsl:when test="@val='1'">
						PartiallyFilled;
					</xsl:when>
					<xsl:when test="@val='2'">
						Filled;
					</xsl:when>
					<xsl:when test="@val='3'">
						DoneForTheDay;
					</xsl:when>
					<xsl:when test="@val='4'">
						Canceled;
					</xsl:when>
					<xsl:when test="@val='5'">
						Replaced;
					</xsl:when>
					<xsl:when test="@val='6'">
						PendingCancelReplace;
					</xsl:when>
					<xsl:when test="@val='7'">
						Stopped;
					</xsl:when>
					<xsl:when test="@val='8'">
						Rejected;
					</xsl:when>
					<xsl:when test="@val='9'">
						Suspended;
					</xsl:when>
					<xsl:when test="@val='A'">
						PendingNew;
					</xsl:when>
					<xsl:when test="@val='B'">
						Calculated;
					</xsl:when>
					<xsl:when test="@val='C'">
						Expired;
					</xsl:when>
					<xsl:when test="@val='D'">
						Restated;
					</xsl:when>
					<xsl:otherwise>
						<xsl:value-of select="@val"/>;
					</xsl:otherwise>
					</xsl:choose>
				</xsl:when>
				<xsl:when test="@tag='151'">
					LeavesQty=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='113'">
					ReportToExch=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='135'">
					OfferSize=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='133'">
					OfferPx=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='134'">
					BidSize=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='132'">
					BidPx=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='131'">
					QuoteReqID=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='9136'">
					QuoteUpdateDesc=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='9137'">
					QuoteRejReason=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='117'">
					QuoteID:
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='270'">
					MDEntryPx=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='271'">
					MDEntrySz=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='278'">
					MDEntryID=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='280'">
					MDEntryRefID=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='279'">
					MDUpdateAction=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='269'">
					MDEntryType=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='268'">
					NoMDEntries:
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='320'">
					SecurityReqID=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='321'">
					SecurityRequestType=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='322'">
					SecurityResponseID=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='323'">
					SecurityResponseType=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='146'">
					NoRelatedSym=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='262'">
					ReqTag=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='266'">
					AggregateBook=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='263'">
					SubscriptionRequestType=
					<xsl:choose>
					<xsl:when test="@val='1'">
						Subscribe;
					</xsl:when>
					<xsl:when test="@val='2'">
						Desubscribe;
					</xsl:when>
					<xsl:when test="@val='3'">
						Snapshot;
					</xsl:when>
					<xsl:otherwise>
						<xsl:value-of select="@val"/>;
					</xsl:otherwise>
					</xsl:choose>
				</xsl:when>
				<xsl:when test="@tag='264'">
					ReqBookType=
					<xsl:choose>
					<xsl:when test="@val='0'">
						Deep;
					</xsl:when>
					<xsl:when test="@val='1'">
						Top;
					</xsl:when>
					<xsl:when test="@val='2'">
						IB;
					</xsl:when>
					<xsl:otherwise>
						<xsl:value-of select="@val"/>;
					</xsl:otherwise>
					</xsl:choose>
				</xsl:when>
				<xsl:when test="@tag='61'">
					Urgency=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='148'">
					Headline=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='231'">
					ContractMultiplier=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='142'">
					SenderLocationID:
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='116'">
					OnBehalfOfSubID=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='109'">
					ClientID=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='111'">
					HotBackupAlarmRequest=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='636'">
					WorkingIndicator:
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='6000'">
					InstrumentType=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='6001'">
					OptionType=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='6002'">
					StrikePrice=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='6003'">
					Expiry=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='6004'">
					Exchange=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='6005'">
					CarryFirm=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='6006'">
					CarryFirmSubAccount=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='6007'">
					CustFirm=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='6008'">
					ContractID=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='6009'">
					ConQPath=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='6010'">
					OrderReference=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='6011'">
					IBRejectReason=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='6012'">
					IBStatus=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='6013'">
					ExecComponent=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='6013'">
					OrderGroup=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='6014'">
					IndicativePrice=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='6015'">
					OAttrib=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='6016'">
					TradeReaderNo=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='6017'">
					OCAGroup=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='6018'">
					legPath=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='6019'">
					NoMarketRules=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='6020'">
					MRNegativeCapable=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='6021'">
					MRPriceMagnification=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='6022'">
					MRNoPriceDisplayIntervals=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='6023'">
					MRLowEdge=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='6024'">
					MRIntegralDigits=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='6025'">
					MRFractionalDigits=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='6026'">
					MRNoPriceIncrementIntervals=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='6027'">
					MRIncrement=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='6028'">
					MRSizeMagnification=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='6029'">
					MRNoSizeDisplayIntervals=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='6030'">
					MRNoSizeIncrementIntervals=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='6031'">
					MRIdent=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='6032'">
					MDNosCompressedBits=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='6033'">
					MDCompressedData=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='6034'">
					TWSVersion=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='6035'">
					IBLocalSymbol=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='6036'">
					AccountRequest=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='6037'">
					OptionOrigin=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='6038'">
					LastSecurityDefinition=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='6039'">
					BestExEligible=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='6040'">
					SubMsgType=
					<xsl:choose>
					<xsl:when test="@val='2'">
						LinkageOrderId;
					</xsl:when>
					<xsl:when test="@val='3'">
						FairPriceRequest;
					</xsl:when>
					<xsl:when test="@val='4'">
						VwapTime;
					</xsl:when>
					<xsl:when test="@val='5'">
						SecDefDates;
					</xsl:when>
					<xsl:when test="@val='6'">
						AccountRequest;
					</xsl:when>
					<xsl:when test="@val='7'">
						CombLegComfirmation;
					</xsl:when>
					<xsl:when test="@val='8'">
						MissedMktData;
					</xsl:when>
					<xsl:when test="@val='9'">
						SymbolLookupQuery;
					</xsl:when>
					<xsl:when test="@val='10'">
						WhatIfMargin;
					</xsl:when>
					<xsl:when test="@val='11'">
						Bundle;
					</xsl:when>
					<xsl:when test="@val='12'">
						Realloc;
					</xsl:when>
					<xsl:when test="@val='13'">
						OptionMoneyQuery;
					</xsl:when>
					<xsl:when test="@val='14'">
						Dvp;
					</xsl:when>
					<xsl:when test="@val='15'">
						DvpInfo;
					</xsl:when>
					<xsl:when test="@val='16'">
						FAPositions;
					</xsl:when>
					<xsl:when test="@val='17'">
						DebugInfo;
					</xsl:when>
					<xsl:when test="@val='18'">
						UpdateCCPTime;
					</xsl:when>
					<xsl:when test="@val='19'">
						XML;
					</xsl:when>
					<xsl:when test="@val='20'">
						XML;
					</xsl:when>
					<xsl:when test="@val='21'">
						XML;
					</xsl:when>
					<xsl:when test="@val='22'">
						XML;
					</xsl:when>
					<xsl:when test="@val='23'">
						FAAutoProfile;
					</xsl:when>
					<xsl:when test="@val='24'">
						ExcludeFromBest;
					</xsl:when>
					<xsl:when test="@val='25'">
						RfqSize;
					</xsl:when>
					<xsl:when test="@val='26'">
						DeltaNeutralValidate;
					</xsl:when>
					<xsl:when test="@val='30'">
						XmlQuery;
					</xsl:when>
					<xsl:otherwise>
						<xsl:value-of select="@val"/>;
					</xsl:otherwise>
					</xsl:choose>	
				</xsl:when>
				<xsl:when test="@tag='6041'">
					ExchPrefs=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='6042'">
					LinkageOrderId=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='6043'">
					Linkage=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='6044'">
					LinkageType=
					<xsl:choose>
					<xsl:when test="@val='0'">
						P;
					</xsl:when>
					<xsl:when test="@val='1'">
						PA;
					</xsl:when>
					<xsl:when test="@val='2'">
						Non-linkage;
					</xsl:when>
					<xsl:otherwise>
						<xsl:value-of select="@val"/>;
					</xsl:otherwise>
					</xsl:choose>	
				</xsl:when>
				<xsl:when test="@tag='6045'">
					DpmExchange=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='6046'">
					ValidExchanges=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='6047'">
					FairPrice=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='6048'">
					LeadFutExpConID=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='6049'">
					LeadFutExpDate=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='6050'">
					DeepExchanges=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='6051'">
					ThiAffil=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='6052'">
					SystemDefaultSizes=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='6053'">
					PrivLabCoName=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='6054'">
					PrivLabProdName=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='6055'">
					PrivLabFaxNo=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='6056'">
					PrivLabUrls=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='6057'">
					PrivHelpDesk=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='6058'">
					TradingClass=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='6059'">
					Reason=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='6060'">
					SendResponse=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='6061'">
					VwapTime=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='6062'">
					Indicative=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='9703'">
					TradingSessionID=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='9702'">
					CtiCode=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='9707'">
					GiveUpFirm=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='9708'">
					CmtaGiveupCD=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='6076'">
					BDSymbols=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='6083'">
					MaxMktData=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='6084'">
					CcpVersion=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='8001'">
					FirstKey=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='8002'">
					SecondKey=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='8003'">
					ThirdKey=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='8004'">
					Value=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='6065'">
					MarketPrice=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='6067'">
					MarketValue=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='6068'">
					Description=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='6064'">
					Position=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='6088'">
					EOrder=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='6091'">
					WhatIf=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='6095'">
					AcctCode=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='6096'">
					FamilyCode=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='6097'">
					Reallocs=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='6098'">
					ExecIds=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='9800'">
					IboTypes=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='9804'">
					Dvp=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='6077'">
					BrokerDealer=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='6105'">
					ActivationPrice=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='6106'">
					TrailingClientId=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='6107'">
					ParentClientId=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='6102'">
					SweepToFill=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='6103'">
					Reserved/DisplaySize=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='9805'">
					BdType=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='9811'">
					BrokerDealer=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='6089'">
					MaxMsgsPerSec=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='6090'">
					AnyExchOk=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='6102'">
					SweepToFill=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='6103'">
					DisplaySize=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='6104'">
					LogoFileName=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='6105'">
					ActivationPrice=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='6106'">
					TrailingClientId=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='6107'">
					ParentClientId=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='6108'">
					FA=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='6131'">
					Submitter=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='9805'">
					BDType=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='9804'">
					DVP=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='9812'">
					LastResetTime=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='6117'">
					StopPrice=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='6122'">
					OptionAcct=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='6130'">
					Chameleon=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='6132'">
					PooledAcct=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='6138'">
					Ibsx=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='6139'">
					Mibsx=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='6140'">
					Sizeop=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='6141'">
					PrivLabFrameIconImageName=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='6142'">
					PrivLabInitUrl=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='6119'">
					ServerId=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='6120'">
					ComboRules=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='6121'">
					DdeId=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='9813'">
					DiscretionaryAmt=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='9814'">
					Retail=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='9881'">
					BTOrderInst=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='22'">
					SecurityIDSource=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='440'">
					ClearingAccount=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='439'">
					ClearingFirm=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='583'">
					ClOrdLinkID=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='9815'">
					LastLoginTime=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='9801'">
					BlockOrder=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='6151'">
					StockRefPrice=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='6152'">
					StockRangeLower=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='6153'">
					StockRangeUpper=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='6154'">
					Delta=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='432'">
					GoodTilDate=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='6118'">
					XML=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='41'">
					OrigClOrdID=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='9817'">
					ConvertToUnderExch=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='126'">
					ExpireTime=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='122'">
					OrigSendingTime=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='6159'">
					FAMethod=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='6160'">
					FAGroup=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='6161'">
					FAProfile=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='6164'">
					FAPct=
					<xsl:value-of select="@val"/>;
				</xsl:when>
				<xsl:when test="@tag='43'">
				</xsl:when>			
				<xsl:when test="@tag='40'">
				</xsl:when>		
				<xsl:when test="@tag='55'">
				</xsl:when>	
				<xsl:when test="@tag='37'">
				</xsl:when>	
				<xsl:when test="@tag='11'">
				</xsl:when>
				<xsl:when test="@tag='54'">
				</xsl:when>
				<xsl:when test="@tag='38'">
				</xsl:when>
				<xsl:when test="@tag='52'">
				</xsl:when>
				<xsl:when test="@tag='44'">
				</xsl:when>
				<xsl:when test="@tag='32'">
				</xsl:when>	
				<xsl:when test="@tag='31'">
				</xsl:when>
				<xsl:when test="@tag='59'">
				</xsl:when>		
				<xsl:when test="@tag='200'">
				</xsl:when>																		
				<xsl:when test="@tag='198'">SecondaryOrderID= <xsl:value-of select="@val"/>; </xsl:when>
				<xsl:when test="@tag='378'">ExecRestatementReason= <xsl:value-of select="@val"/>; </xsl:when>
				<xsl:when test="@tag='541'">MaturityDate= <xsl:value-of select="@val"/>; </xsl:when>
				<xsl:when test="@tag='851'">LastLiquidityInd= <xsl:value-of select="@val"/>; </xsl:when>
				<xsl:when test="@tag='6115'">TriggerMethod= <xsl:value-of select="@val"/>; </xsl:when>
				<xsl:when test="@tag='6116'">IgnoreRth= <xsl:value-of select="@val"/>; </xsl:when>
				<xsl:when test="@tag='6123'">CondConid= <xsl:value-of select="@val"/>; </xsl:when>
				<xsl:when test="@tag='6124'">CondExch= <xsl:value-of select="@val"/>; </xsl:when>
				<xsl:when test="@tag='6125'">CondPrice= <xsl:value-of select="@val"/>; </xsl:when>
				<xsl:when test="@tag='6126'">CondOp= <xsl:value-of select="@val"/>; </xsl:when>
				<xsl:when test="@tag='6128'">CondIgnoreRth= <xsl:value-of select="@val"/>; </xsl:when>
				<xsl:when test="@tag='6136'">CondListSize= <xsl:value-of select="@val"/>; </xsl:when>
				<xsl:when test="@tag='6137'">CondLogicBind= <xsl:value-of select="@val"/>; </xsl:when>
				<xsl:when test="@tag='6156'">BasketOrder= <xsl:value-of select="@val"/>; </xsl:when>
				<xsl:when test="@tag='6166'">CondStrike= <xsl:value-of select="@val"/>; </xsl:when>
				<xsl:when test="@tag='6168'">CondExpiry= <xsl:value-of select="@val"/>; </xsl:when>
				<xsl:when test="@tag='6169'">CondSecurityType= <xsl:value-of select="@val"/>; </xsl:when>
				<xsl:when test="@tag='6205'">OnlyRTH= <xsl:value-of select="@val"/>; </xsl:when>
				<xsl:when test="@tag='6210'">TWSTickerExchange= <xsl:value-of select="@val"/>; </xsl:when>
				<xsl:when test="@tag='6211'">ParentAlertId= <xsl:value-of select="@val"/>; </xsl:when>
				<xsl:when test="@tag='6220'">CondContractMultiplier= <xsl:value-of select="@val"/>; </xsl:when>
				<xsl:when test="@tag='6222'">CondType= <xsl:value-of select="@val"/>; </xsl:when>
				<xsl:when test="@tag='6223'">CondTime= <xsl:value-of select="@val"/>; </xsl:when>
				<xsl:when test="@tag='6224'">CondSendEmail= <xsl:value-of select="@val"/>; </xsl:when>
				<xsl:when test="@tag='6226'">CondEmailText= <xsl:value-of select="@val"/>; </xsl:when>
				<xsl:when test="@tag='6227'">CondTWSActions= <xsl:value-of select="@val"/>; </xsl:when>
				<xsl:when test="@tag='6236'">ExtWorkingIndicator= <xsl:value-of select="@val"/>; </xsl:when>
				<xsl:when test="@tag='6238'">AlertActionOnTrigger= <xsl:value-of select="@val"/>; </xsl:when>
				<xsl:when test="@tag='6241'">CondInactive= <xsl:value-of select="@val"/>; </xsl:when>
				<xsl:when test="@tag='6245'">CondPercentage= <xsl:value-of select="@val"/>; </xsl:when>
				<xsl:when test="@tag='6246'">CondExecutionPattern= <xsl:value-of select="@val"/>; </xsl:when>
				<xsl:when test="@tag='6263'">CondMktVolume= <xsl:value-of select="@val"/>; </xsl:when>
				<xsl:when test="@tag='6268'">TrailingAmtUnit= <xsl:value-of select="@val"/>; </xsl:when>
				<xsl:when test="@tag='6287'">NotHeld= <xsl:value-of select="@val"/>; </xsl:when>
				<xsl:when test="@tag='6289'">CurrentPrice= <xsl:value-of select="@val"/>; </xsl:when>
				<xsl:when test="@tag='6408'">PageName= <xsl:value-of select="@val"/>; </xsl:when>
				<xsl:when test="@tag='6419'">ClrIntent= <xsl:value-of select="@val"/>; </xsl:when>
				<xsl:when test="@tag='6433'">OutsideRTH= <xsl:value-of select="@val"/>; </xsl:when>
				<xsl:when test="@tag='6436'">DeactiveOnClose= <xsl:value-of select="@val"/>; </xsl:when>
				<xsl:when test="@tag='6521'">Deactivate= <xsl:value-of select="@val"/>; </xsl:when>
				<xsl:when test="@tag='6532'">CustomerOrderTime= <xsl:value-of select="@val"/>; </xsl:when>
				<xsl:when test="@tag='6561'">TwsAlgoName= <xsl:value-of select="@val"/>; </xsl:when>
				<xsl:when test="@tag='6568'">ExchangeExecID= <xsl:value-of select="@val"/>; </xsl:when>
				<xsl:when test="@tag='6569'">ExchangeOrderID= <xsl:value-of select="@val"/>; </xsl:when>
				<xsl:when test="@tag='6571'">OrderReceiptTime= <xsl:value-of select="@val"/>; </xsl:when>
				<xsl:when test="@tag='6579'">CondSubmitCancel= <xsl:value-of select="@val"/>; </xsl:when>
				<xsl:when test="@tag='6596'">BrokerExpireTime= <xsl:value-of select="@val"/>; </xsl:when>
				<xsl:when test="@tag='6637'">ActiveOrderQty= <xsl:value-of select="@val"/>; </xsl:when>
				<xsl:when test="@tag='6661'">DeactiveOnDisconnect= <xsl:value-of select="@val"/>; </xsl:when>
				<xsl:when test="@tag='6664'">TwsAlgoXml= <xsl:value-of select="@val"/>; </xsl:when>
				<xsl:when test="@tag='6816'">FirstExecReceiveTime= <xsl:value-of select="@val"/>; </xsl:when>
				<xsl:when test="@tag='6817'">OrigOrderReceiptTime= <xsl:value-of select="@val"/>; </xsl:when>
				<xsl:when test="@tag='6947'">CondTimeZone= <xsl:value-of select="@val"/>; </xsl:when>
				<xsl:when test="@tag='8032'">IBKRATS= <xsl:value-of select="@val"/>; </xsl:when>
				<xsl:when test="@tag='8043'">LastTradePrice= <xsl:value-of select="@val"/>; </xsl:when>
				<xsl:when test="@tag='8109'">LastRecvExecTime= <xsl:value-of select="@val"/>; </xsl:when>
				<xsl:when test="@tag='8339'">PriceMgmtAlgo= <xsl:value-of select="@val"/>; </xsl:when>
				<xsl:when test="@tag='8402'">Duration= <xsl:value-of select="@val"/>; </xsl:when>
				<xsl:when test="@tag='8403'">EvenMidOffset= <xsl:value-of select="@val"/>; </xsl:when>
				<xsl:when test="@tag='8404'">OddMidOffset= <xsl:value-of select="@val"/>; </xsl:when>
				<xsl:when test="@tag='8405'">PostToATS= <xsl:value-of select="@val"/>; </xsl:when>
				<xsl:when test="@tag='9822'">PercentOffset= <xsl:value-of select="@val"/>; </xsl:when>
				<xsl:otherwise>				
				<xsl:value-of select="@tag"/> =
				<xsl:value-of select="@val"/>;
			</xsl:otherwise>
			</xsl:choose>
			</xsl:for-each>
			</td>
		</tr>
	</xsl:template>
</xsl:stylesheet>
