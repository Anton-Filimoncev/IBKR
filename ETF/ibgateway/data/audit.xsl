<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<!-- Audit Trail Convertion Stylesheet @Date: 12/01/03 @Author: Ahmet Bozkurt -->
	<xsl:template match="/">
		<html>
			<head><title>Audit Trail</title></head>
			<body>
				<xsl:apply-templates/>
			</body>
		</html>
	</xsl:template>
	
	<xsl:template match="Entry">
		<p>
		<table border="1">
			<tr>	<!-- Table Header Row -->
				<th><xsl:value-of select="@type"/></th>
			</tr>
			<xsl:for-each select="field">
			<tr>
			<xsl:choose>
				<!--
					Need to create several templates for tag ranges to avoid the
					"ClassGenException: Branch target offset too large for short"
					error in Xalan.
					Add new tags to the appropriate template.  Break up existing
					ranges if they get too long.  Make sure there is an
					'otherwise' branch in each range.
				-->
				<xsl:when test="@tag &lt;= '999'">
					<xsl:call-template name="tags_up_to_999"/>
				</xsl:when>
				<xsl:when test="@tag &lt;= '5999'">
					<xsl:call-template name="tags_up_to_5999"/>
				</xsl:when>
				<xsl:when test="@tag &lt;= '6999'">
					<xsl:call-template name="tags_up_to_6999"/>
				</xsl:when>
				<xsl:when test="@tag &lt;= '9999'">
					<xsl:call-template name="tags_up_to_9999"/>
				</xsl:when>
				<xsl:otherwise>
					<xsl:call-template name="unknown_tag"/>
				</xsl:otherwise>
			</xsl:choose>
			</tr>
			</xsl:for-each>
		</table>
	</p>
	</xsl:template>

	<xsl:template name="tags_up_to_999">
		<xsl:choose>
				<xsl:when test="@tag='198'">
					<td>SecondaryOrderID</td>
					<td><xsl:value-of select="@val"/></td>
				</xsl:when>
				<xsl:when test="@tag='378'">
					<td>ExecRestatementReason</td>
					<td><xsl:value-of select="@val"/></td>
				</xsl:when>
				<xsl:when test="@tag='541'">
					<td>MaturityDate</td>
					<td><xsl:value-of select="@val"/></td>
				</xsl:when>
				<xsl:when test="@tag='35'">
					<td>MsgType</td>
					<xsl:choose>
						<xsl:when test="@val='0'">
							<td>HeartBeat</td>
						</xsl:when>
						<xsl:when test="@val='1'">
							<td>TestRequest</td>
						</xsl:when>
						<xsl:when test="@val='2'">
							<td>ResendRequest</td>
						</xsl:when>
						<xsl:when test="@val='3'">
							<td>Reject</td>
						</xsl:when>
						<xsl:when test="@val='4'">
							<td>SequenceReset</td>
						</xsl:when>
						<xsl:when test="@val='5'">
							<td>Logout</td>
						</xsl:when>
						<xsl:when test="@val='8'">
							<td>ExecutionReport</td>
						</xsl:when>
						<xsl:when test="@val='9'">
							<td>OrderCancelReject</td>
						</xsl:when>
						<xsl:when test="@val='A'">
							<td>Logon</td>
						</xsl:when>
						<xsl:when test="@val='D'">
							<td>NewOrderSingle</td>
						</xsl:when>
						<xsl:when test="@val='F'">
							<td>OrderCancelRequest</td>
						</xsl:when>
						<xsl:when test="@val='G'">
							<td>OrderCancelReplaceRequest</td>
						</xsl:when>
						<xsl:when test="@val='H'">
							<td>OrderStatusRequest</td>
						</xsl:when>
						<xsl:when test="@val='U'">
							<td>UserDefined</td>
						</xsl:when>
						<xsl:when test="@val='R'">
							<td>QuoteRequest</td>
						</xsl:when>
						<xsl:when test="@val='S'">
							<td>Quote</td>
						</xsl:when>
						<xsl:when test="@val='X'">
							<td>ArcaQuote</td>
						</xsl:when>
						<xsl:when test="@val='Y'">
							<td>DeepQuote</td>
						</xsl:when>
						<xsl:when test="@val='Z'">
							<td>IBOrder</td>
						</xsl:when>
						<xsl:when test="@val='W'">
							<td>BestOptMktQuote</td>
						</xsl:when>
						<xsl:when test="@val='c'">
							<td>SecurityDefinitionRequest</td>
						</xsl:when>
						<xsl:when test="@val='V'">
							<td>MarketDataRequest</td>
						</xsl:when>
						<xsl:when test="@val='d'">
							<td>SecurityDefinition</td>
						</xsl:when>
						<xsl:when test="@val='B'">
							<td>News</td>
						</xsl:when>
						<xsl:otherwise>
							<td><xsl:value-of select="@val"/></td>
						</xsl:otherwise>
					</xsl:choose>	
				</xsl:when>	
				<xsl:when test="@tag='7'">
					<td>BeginSeqNo</td>
					<td><xsl:value-of select="@val"/></td>
				</xsl:when>
				<xsl:when test="@tag='15'">
					<td>Currency</td>
					<td><xsl:value-of select="@val"/></td>
				</xsl:when>
				<xsl:when test="@tag='11'">
					<td>ClientOrderID</td>
					<td><xsl:value-of select="@val"/></td>
				</xsl:when>
				<xsl:when test="@tag='16'">
					<td>EndSeqNo</td>
					<td><xsl:value-of select="@val"/></td>
				</xsl:when>
				<xsl:when test="@tag='17'">
					<td>ExecID</td>
					<td><xsl:value-of select="@val"/></td>
				</xsl:when>
				<xsl:when test="@tag='30'">
					<td>LastMarket</td>
					<td><xsl:value-of select="@val"/></td>
				</xsl:when>
				<xsl:when test="@tag='57'">
					<td>TargetSubID</td>
					<td><xsl:value-of select="@val"/></td>
				</xsl:when>
				<xsl:when test="@tag='50'">
					<td>SenderSubID</td>
					<td><xsl:value-of select="@val"/></td>
				</xsl:when>
				<xsl:when test="@tag='34'">
				</xsl:when>
				<xsl:when test="@tag='97'">
					<td>PossResend</td>
					<td><xsl:value-of select="@val"/></td>
				</xsl:when>
				<xsl:when test="@tag='52'">
					<td>SendingTime</td>
					<td><xsl:value-of select="@val"/></td>
				</xsl:when>
				<xsl:when test="@tag='122'">
				</xsl:when>
				<xsl:when test="@tag='10'">
					<td>CheckSum</td>
					<td><xsl:value-of select="@val"/></td>
				</xsl:when>
				<xsl:when test="@tag='98'">
					<td>EncryptMethod</td>
					<td><xsl:value-of select="@val"/></td>
				</xsl:when>
				<xsl:when test="@tag='108'">
					<td>HeartBtInt</td>
					<td><xsl:value-of select="@val"/></td>
				</xsl:when>
				<xsl:when test="@tag='58'">
					<td>Text</td>
					<td><xsl:value-of select="@val"/></td>
				</xsl:when>
				<xsl:when test="@tag='45'">
					<td>RefSeqNo</td>
					<td><xsl:value-of select="@val"/></td>
				</xsl:when>
				<xsl:when test="@tag='123'">
					<td>GapFillFlag</td>
					<td><xsl:value-of select="@val"/></td>
				</xsl:when>
				<xsl:when test="@tag='36'">
					<td>NewSeqNum</td>
					<td><xsl:value-of select="@val"/></td>
				</xsl:when>
				<xsl:when test="@tag='112'">
					<td>TestReqID</td>
					<td><xsl:value-of select="@val"/></td>
				</xsl:when>
				<xsl:when test="@tag='102'">
					<td>CxlRejReason</td>
					<td><xsl:value-of select="@val"/></td>
				</xsl:when>
				<xsl:when test="@tag='37'">
					<td>OrderID</td>
					<td><xsl:value-of select="@val"/></td>
				</xsl:when>
				<xsl:when test="@tag='20'">
					<td>ExecTransType</td>
					<xsl:choose>
						<xsl:when test="@val='0'">
							<td>New</td>
						</xsl:when>
						<xsl:when test="@val='1'">
							<td>Cancel</td>
						</xsl:when>
						<xsl:when test="@val='2'">
							<td>Correct</td>
						</xsl:when>
						<xsl:when test="@val='3'">
							<td>Status</td>
						</xsl:when>
						<xsl:when test="@val='z'">
							<td>SplitBust</td>
						</xsl:when>
						<xsl:otherwise>
							<td><xsl:value-of select="@val"/></td>
						</xsl:otherwise>
					</xsl:choose>
				</xsl:when>

				<xsl:when test="@tag='19'">
					<td>ExecRefID</td>
					<td><xsl:value-of select="@val"/></td>
				</xsl:when>
				<xsl:when test="@tag='39'">
					<td>OrdStatus</td>
					<xsl:choose>
					<xsl:when test="@val='0'">
						<td>New</td>
					</xsl:when>
					<xsl:when test="@val='1'">
						<td>PartiallyFilled</td>
					</xsl:when>
					<xsl:when test="@val='2'">
						<td>Filled</td>
					</xsl:when>
					<xsl:when test="@val='3'">
						<td>DoneForTheDay</td>
					</xsl:when>
					<xsl:when test="@val='4'">
						<td>Canceled</td>
					</xsl:when>
					<xsl:when test="@val='5'">
						<td>Replaced</td>
					</xsl:when>
					<xsl:when test="@val='6'">
						<td>PendingCancelReplace</td>
					</xsl:when>
					<xsl:when test="@val='7'">
						<td>Stopped</td>
					</xsl:when>
					<xsl:when test="@val='8'">
						<td>Rejected</td>
					</xsl:when>
					<xsl:when test="@val='9'">
						<td>Suspended</td>
					</xsl:when>
					<xsl:when test="@val='A'">
						<td>PendingNew</td>
					</xsl:when>
					<xsl:when test="@val='B'">
						<td>Calculated</td>
					</xsl:when>
					<xsl:when test="@val='C'">
						<td>Expired</td>
					</xsl:when>
					<xsl:when test="@val='D'">
						<td>PendingCancel</td>
					</xsl:when>
					<xsl:otherwise>
						<td><xsl:value-of select="@val"/></td>
					</xsl:otherwise>
					</xsl:choose>	
				</xsl:when>
				<xsl:when test="@tag='55'">
					<td>Symbol</td>
					<td><xsl:value-of select="@val"/></td>
				</xsl:when>
				<xsl:when test="@tag='54'">
					<td>Side</td>
					<xsl:choose>
					<xsl:when test="@val='1'">
						<td>Buy</td>
					</xsl:when>
					<xsl:when test="@val='2'">
						<td>Sell</td>
					</xsl:when>
					<xsl:when test="@val='3'">
						<td>BuyMinus</td>
					</xsl:when>
					<xsl:when test="@val='4'">
						<td>SellPlus</td>
					</xsl:when>
					<xsl:when test="@val='5'">
						<td>SellShort</td>
					</xsl:when>
					<xsl:otherwise>
						<td><xsl:value-of select="@val"/></td>
					</xsl:otherwise>
					</xsl:choose>	
				</xsl:when>
				<xsl:when test="@tag='38'">
					<td>OrderQty</td>
					<td><xsl:value-of select="@val"/></td>
				</xsl:when>
				<xsl:when test="@tag='32'">
					<td>LastShares</td>
					<td><xsl:value-of select="@val"/></td>
				</xsl:when>
				<xsl:when test="@tag='31'">
					<td>LastPx</td>
					<td><xsl:value-of select="@val"/></td>
				</xsl:when>
				<xsl:when test="@tag='14'">
					<td>CumQty</td>
					<td><xsl:value-of select="@val"/></td>
				</xsl:when>
				<xsl:when test="@tag='6'">
					<td>AvgPx</td>
					<td><xsl:value-of select="@val"/></td>
				</xsl:when>
				<xsl:when test="@tag='60'">
					<td>TransactTime</td>
					<td><xsl:value-of select="@val"/></td>
				</xsl:when>
				<xsl:when test="@tag='40'">
					<td>OrderType</td>
					<xsl:choose>
					<xsl:when test="@val='0'">
						<td>None</td>
					</xsl:when>
					<xsl:when test="@val='1'">
						<td>Market</td>
					</xsl:when>
					<xsl:when test="@val='2'">
						<td>Limit</td>
					</xsl:when>
					<xsl:when test="@val='3'">
						<td>Stop</td>
					</xsl:when>
					<xsl:when test="@val='4'">
						<td>StopLimit</td>
					</xsl:when>
					<xsl:when test="@val='5'">
						<td>MOC</td>
					</xsl:when>
					<xsl:when test="@val='6'">
						<td>WithOrWithout</td>
					</xsl:when>
					<xsl:when test="@val='7'">
						<td>LimitOrBetter</td>
					</xsl:when>
					<xsl:when test="@val='8'">
						<td>LimitWithOrWithout</td>
					</xsl:when>
					<xsl:when test="@val='9'">
						<td>OnBasis</td>
					</xsl:when>
					<xsl:when test="@val='A'">
						<td>OnClose</td>
					</xsl:when>
					<xsl:when test="@val='B'">
						<td>LOC</td>
					</xsl:when>
					<xsl:when test="@val='C'">
						<td>ForexMarket</td>
					</xsl:when>
					<xsl:when test="@val='D'">
						<td>PreviouslyQuoted</td>
					</xsl:when>
					<xsl:when test="@val='E'">
						<td>Relative</td>
					</xsl:when>
					<xsl:when test="@val='F'">
						<td>RelativeToStock</td>
					</xsl:when>
					<xsl:when test="@val='G'">
						<td>ForexSwap</td>
					</xsl:when>
					<xsl:when test="@val='H'">
						<td>ForexPreviouslyQuoted</td>
					</xsl:when>
					<xsl:when test="@val='I'">
						<td>Funari</td>
					</xsl:when>
					<xsl:when test="@val='K'">
						<td>Market2Limit</td>
					</xsl:when>
					<xsl:when test="@val='Q'">
						<td>QuoteRequest</td>
					</xsl:when>
					<xsl:when test="@val='T'">
						<td>TrailingStop</td>
					</xsl:when>
					<xsl:when test="@val='P'">
						<td>Pegged</td>
					</xsl:when>
					<xsl:otherwise>
						<td><xsl:value-of select="@val"/></td>
					</xsl:otherwise>
					</xsl:choose>	
				</xsl:when>
				<xsl:when test="@tag='44'">
					<td>LmtPrice</td>
					<td><xsl:value-of select="@val"/></td>
				</xsl:when>
				<xsl:when test="@tag='99'">
					<td>AuxPrice</td>
					<td><xsl:value-of select="@val"/></td>
				</xsl:when>
				<xsl:when test="@tag='59'">
					<td>TimeInForce</td>
					<xsl:choose>
					<xsl:when test="@val='0'">
						<td>DAY</td>
					</xsl:when>
					<xsl:when test="@val='1'">
						<td>GTC</td>
					</xsl:when>
					<xsl:when test="@val='2'">
						<td>OPG</td>
					</xsl:when>
					<xsl:when test="@val='3'">
						<td>IOC</td>
					</xsl:when>
					<xsl:when test="@val='4'">
						<td>FOK</td>
					</xsl:when>
					<xsl:when test="@val='5'">
						<td>GTX</td>
					</xsl:when>
					<xsl:when test="@val='6'">
						<td>GTD</td>
					</xsl:when>
					<xsl:when test="@val='7'">
						<td>CLG</td>
					</xsl:when>
					<xsl:when test="@val='8'">
						<td>AUC</td>
					</xsl:when>
					<xsl:otherwise>
						<td><xsl:value-of select="@val"/></td>
					</xsl:otherwise>
					</xsl:choose>
				</xsl:when>
				<xsl:when test="@tag='47'">
					<td>Rule80A</td>
					<xsl:choose>
					<xsl:when test="@val='A'">
						<td>AgenySingleOrder</td>
					</xsl:when>
					<xsl:when test="@val='Y'">
						<td>ProgramOrder</td>
					</xsl:when>
					<xsl:otherwise>
							<td><xsl:value-of select="@val"/></td>
					</xsl:otherwise>
					</xsl:choose>
				</xsl:when>	
				<xsl:when test="@tag='77'">
						<td>OpenClose</td>
						<xsl:choose>
						<xsl:when test="@val='O'">
							<td>Open</td>
						</xsl:when>
						<xsl:when test="@val='C'">
							<td>Close</td>
						</xsl:when>
						<xsl:otherwise>
							<td><xsl:value-of select="@val"/></td>
						</xsl:otherwise>
						</xsl:choose>
				</xsl:when>
				<xsl:when test="@tag='103'">
					<td>OrdRejReason</td>
					<td><xsl:value-of select="@val"/></td>
				</xsl:when>
				<xsl:when test="@tag='41'">
					<td>OrigClOrdID</td>
					<td><xsl:value-of select="@val"/></td>
				</xsl:when>
				<xsl:when test="@tag='125'">
					<td>CxlType</td>
					<td><xsl:value-of select="@val"/></td>
				</xsl:when>
				<xsl:when test="@tag='48'">
					<td>SecurityID</td>
					<td><xsl:value-of select="@val"/></td>
				</xsl:when>
				<xsl:when test="@tag='141'">
					<td>ResetSeqNumFlag</td>
					<td><xsl:value-of select="@val"/></td>
				</xsl:when>
				<xsl:when test="@tag='207'">
					<td>SecurityExchange</td>
					<td><xsl:value-of select="@val"/></td>
				</xsl:when>
				<xsl:when test="@tag='167'">
					<td>SecurityType</td>
					<td><xsl:value-of select="@val"/></td>
				</xsl:when>
				<xsl:when test="@tag='201'">
					<td>PutOrCall</td>
					<xsl:choose>
					<xsl:when test="@val='0'">
						<td>PUT</td>
					</xsl:when>
					<xsl:when test="@val='1'">
						<td>CALL</td>
					</xsl:when>
					<xsl:otherwise>
						<td><xsl:value-of select="@val"/></td>
					</xsl:otherwise>
					</xsl:choose>
				</xsl:when>
				<xsl:when test="@tag='200'">
					<td>MaturityMonthYear</td>
					<td><xsl:value-of select="@val"/></td>
				</xsl:when>
				<xsl:when test="@tag='205'">
					<td>MaturityDay</td>
					<td><xsl:value-of select="@val"/></td>
				</xsl:when>
				<xsl:when test="@tag='202'">
					<td>StrikePrice</td>
					<td><xsl:value-of select="@val"/></td>
				</xsl:when>
				<xsl:when test="@tag='204'">
					<td>CustomerOrFirm</td>
					<xsl:choose>
					<xsl:when test="@val='0'">
						<td>Customer</td>
					</xsl:when>
					<xsl:when test="@val='1'">
						<td>Firm</td>
					</xsl:when>
					<xsl:otherwise>
						<td><xsl:value-of select="@val"/></td>
					</xsl:otherwise>
					</xsl:choose>
				</xsl:when>
				<xsl:when test="@tag='96'">
					<td>RawData</td>
					<td><xsl:value-of select="@val"/></td>
				</xsl:when>
				<xsl:when test="@tag='95'">
					<td>RawDataLength</td>
					<td><xsl:value-of select="@val"/></td>
				</xsl:when>
				<xsl:when test="@tag='1'">
					<td>Account</td>
					<td><xsl:value-of select="@val"/></td>
				</xsl:when>
				<xsl:when test="@tag='81'">
					<td>ProcessCode</td>
					<td><xsl:value-of select="@val"/></td>
				</xsl:when>
				<xsl:when test="@tag='18'">
					<td>ExecInst</td>
					<xsl:choose>
					<xsl:when test="@val='1'">
						<td>Notheld</td>
					</xsl:when>
					<xsl:when test="@val='2'">
						<td>Work</td>
					</xsl:when>
					<xsl:when test="@val='3'">
						<td>Goalong</td>
					</xsl:when>
					<xsl:when test="@val='4'">
						<td>OverTheDay</td>
					</xsl:when>
					<xsl:when test="@val='5'">
						<td>Held</td>
					</xsl:when>
					<xsl:when test="@val='6'">
						<td>ParticipateDontInitiate</td>
					</xsl:when>
					<xsl:when test="@val='7'">
						<td>Strictscale</td>
					</xsl:when>
					<xsl:when test="@val='8'">
						<td>TryToScale</td>
					</xsl:when>
					<xsl:when test="@val='9'">
						<td>StayOnBidside</td>
					</xsl:when>
					<xsl:when test="@val='0'">
						<td>StayOnOfferside</td>
					</xsl:when>
					<xsl:when test="@val='A'">
						<td>Nocross</td>
					</xsl:when>
					<xsl:when test="@val='B'">
						<td>OKToCross</td>
					</xsl:when>
					<xsl:when test="@val='C'">
						<td>CallFirst</td>
					</xsl:when>
					<xsl:when test="@val='D'">
						<td>PercentOfVolume</td>
					</xsl:when>
					<xsl:when test="@val='E'">
						<td>DNI</td>
					</xsl:when>
					<xsl:when test="@val='F'">
						<td>DNR</td>
					</xsl:when>
					<xsl:when test="@val='G'">
						<td>AON</td>
					</xsl:when>
					<xsl:when test="@val='I'">
						<td>InstitutionsOnly</td>
					</xsl:when>
					<xsl:when test="@val='L'">
						<td>LastPeg</td>
					</xsl:when>
					<xsl:when test="@val='M'">
						<td>MidPricePeg</td>
					</xsl:when>
					<xsl:when test="@val='N'">
						<td>NonNegotiable</td>
					</xsl:when>
					<xsl:when test="@val='O'">
						<td>OpeningPeg</td>
					</xsl:when>
					<xsl:when test="@val='P'">
						<td>MarketPeg</td>
					</xsl:when>
					<xsl:when test="@val='R'">
						<td>PrimaryPeg</td>
					</xsl:when>
					<xsl:when test="@val='S'">
						<td>Suspend</td>
					</xsl:when>
					<xsl:when test="@val='U'">
						<td>CustomerDisplayInstruction</td>
					</xsl:when>
					<xsl:when test="@val='V'">
						<td>Netting</td>
					</xsl:when>
					<xsl:when test="@val='W'">
						<td>PegToVWAP</td>
					</xsl:when>
					<xsl:when test="@val='X'">
						<td>TradeAlong</td>
					</xsl:when>
					<xsl:when test="@val='Y'">
						<td>TryToStop</td>
					</xsl:when>
					<xsl:when test="@val='Z'">
						<td>CancelIfNotBest</td>
					</xsl:when>
					<xsl:when test="@val='a'">
						<td>TrailingStop</td>
					</xsl:when>
					<xsl:when test="@val='e'">
						<td>Algo</td>
					</xsl:when>
					<xsl:when test="@val='s'">
						<td>PegToStk</td>
					</xsl:when>
					<xsl:otherwise>
						<td><xsl:value-of select="@val"/></td>
					</xsl:otherwise>
					</xsl:choose>
				</xsl:when>
				<xsl:when test="@tag='100'">
					<td>ExDestination</td>
					<td><xsl:value-of select="@val"/></td>
				</xsl:when>
				<xsl:when test="@tag='21'">
					<td>HandlInst</td>
					<td><xsl:value-of select="@val"/></td>
				</xsl:when>
				<xsl:when test="@tag='211'">
					<td>PegDifference</td>
					<td><xsl:value-of select="@val"/></td>
				</xsl:when>
				<xsl:when test="@tag='150'">
					<td>ExecType</td>
					<xsl:choose>
					<xsl:when test="@val='0'">
						<td>New</td>
					</xsl:when>
					<xsl:when test="@val='1'">
						<td>PartiallyFilled</td>
					</xsl:when>
					<xsl:when test="@val='2'">
						<td>Filled</td>
					</xsl:when>
					<xsl:when test="@val='3'">
						<td>DoneForTheDay</td>
					</xsl:when>
					<xsl:when test="@val='4'">
						<td>Canceled</td>
					</xsl:when>
					<xsl:when test="@val='5'">
						<td>Replaced</td>
					</xsl:when>
					<xsl:when test="@val='6'">
						<td>PendingCancelReplace</td>
					</xsl:when>
					<xsl:when test="@val='7'">
						<td>Stopped</td>
					</xsl:when>
					<xsl:when test="@val='8'">
						<td>Rejected</td>
					</xsl:when>
					<xsl:when test="@val='9'">
						<td>Suspended</td>
					</xsl:when>
					<xsl:when test="@val='A'">
						<td>PendingNew</td>
					</xsl:when>
					<xsl:when test="@val='B'">
						<td>Calculated</td>
					</xsl:when>
					<xsl:when test="@val='C'">
						<td>Expired</td>
					</xsl:when>
					<xsl:when test="@val='D'">
						<td>Restated</td>
					</xsl:when>
					<xsl:otherwise>
						<td><xsl:value-of select="@val"/></td>
					</xsl:otherwise>
					</xsl:choose>
				</xsl:when>
				<xsl:when test="@tag='151'">
					<td>LeavesQty</td>
					<td><xsl:value-of select="@val"/></td>
				</xsl:when>
				<xsl:when test="@tag='113'">
					<td>ReportToExch</td>
					<td><xsl:value-of select="@val"/></td>
				</xsl:when>
				<xsl:when test="@tag='135'">
					<td>OfferSize</td>
					<td><xsl:value-of select="@val"/></td>
				</xsl:when>
				<xsl:when test="@tag='133'">
					<td>OfferPx</td>
					<td><xsl:value-of select="@val"/></td>
				</xsl:when>
				<xsl:when test="@tag='134'">
					<td>BidSize</td>
					<td><xsl:value-of select="@val"/></td>
				</xsl:when>
				<xsl:when test="@tag='132'">
					<td>BidPx</td>
					<td><xsl:value-of select="@val"/></td>
				</xsl:when>
				<xsl:when test="@tag='131'">
					<td>QuoteReqID</td>
					<td><xsl:value-of select="@val"/></td>
				</xsl:when>
				<xsl:when test="@tag='117'">
					<td>QuoteID</td>
					<td><xsl:value-of select="@val"/></td>
				</xsl:when>
				<xsl:when test="@tag='270'">
					<td>MDEntryPx</td>
					<td><xsl:value-of select="@val"/></td>
				</xsl:when>
				<xsl:when test="@tag='271'">
					<td>MDEntrySz</td>
					<td><xsl:value-of select="@val"/></td>
				</xsl:when>
				<xsl:when test="@tag='278'">
					<td>MDEntryID</td>
					<td><xsl:value-of select="@val"/></td>
				</xsl:when>
				<xsl:when test="@tag='280'">
					<td>MDEntryRefID</td>
					<td><xsl:value-of select="@val"/></td>
				</xsl:when>
				<xsl:when test="@tag='279'">
					<td>MDUpdateAction</td>
					<td><xsl:value-of select="@val"/></td>
				</xsl:when>
				<xsl:when test="@tag='269'">
					<td>MDEntryType</td>
					<td><xsl:value-of select="@val"/></td>
				</xsl:when>
				<xsl:when test="@tag='268'">
					<td>NoMDEntries</td>
					<td><xsl:value-of select="@val"/></td>
				</xsl:when>
				<xsl:when test="@tag='320'">
					<td>SecurityReqID</td>
					<td><xsl:value-of select="@val"/></td>
				</xsl:when>
				<xsl:when test="@tag='321'">
					<td>SecurityRequestType</td>
					<td><xsl:value-of select="@val"/></td>
				</xsl:when>
				<xsl:when test="@tag='322'">
					<td>SecurityResponseID</td>
					<td><xsl:value-of select="@val"/></td>
				</xsl:when>
				<xsl:when test="@tag='323'">
					<td>SecurityResponseType</td>
					<td><xsl:value-of select="@val"/></td>
				</xsl:when>
				<xsl:when test="@tag='146'">
					<td>NoRelatedSym</td>
					<td><xsl:value-of select="@val"/></td>
				</xsl:when>
				<xsl:when test="@tag='262'">
					<td>ReqTag</td>
					<td><xsl:value-of select="@val"/></td>
				</xsl:when>
				<xsl:when test="@tag='266'">
					<td>AggregateBook</td>
					<td><xsl:value-of select="@val"/></td>
				</xsl:when>
				<xsl:when test="@tag='263'">
					<td>SubscriptionRequestType</td>
					<xsl:choose>
					<xsl:when test="@val='1'">
						<td>Subscribe</td>
					</xsl:when>
					<xsl:when test="@val='2'">
						<td>Desubscribe</td>
					</xsl:when>
					<xsl:when test="@val='3'">
						<td>Snapshot</td>
					</xsl:when>
					<xsl:otherwise>
						<td><xsl:value-of select="@val"/></td>
					</xsl:otherwise>
					</xsl:choose>
				</xsl:when>
				<xsl:when test="@tag='264'">
					<td>ReqBookType</td>
					<xsl:choose>
					<xsl:when test="@val='0'">
						<td>Deep</td>
					</xsl:when>
					<xsl:when test="@val='1'">
						<td>Top</td>
					</xsl:when>
					<xsl:when test="@val='2'">
						<td>IB</td>
					</xsl:when>
					<xsl:otherwise>
						<td><xsl:value-of select="@val"/></td>
					</xsl:otherwise>
					</xsl:choose>
				</xsl:when>
				<xsl:when test="@tag='61'">
					<td>Urgency</td>
					<td><xsl:value-of select="@val"/></td>
				</xsl:when>
				<xsl:when test="@tag='148'">
					<td>Headline</td>
					<td><xsl:value-of select="@val"/></td>
				</xsl:when>
				<xsl:when test="@tag='231'">
					<td>ContractMultiplier</td>
					<td><xsl:value-of select="@val"/></td>
				</xsl:when>
				<xsl:when test="@tag='142'">
					<td>SenderLocationID</td>
					<td><xsl:value-of select="@val"/></td>
				</xsl:when>
				<xsl:when test="@tag='116'">
					<td>OnBehalfOfSubID</td>
					<td><xsl:value-of select="@val"/></td>
				</xsl:when>
				<xsl:when test="@tag='109'">
					<td>ClientID</td>
					<td><xsl:value-of select="@val"/></td>
				</xsl:when>
				<xsl:when test="@tag='111'">
					<td>HotBackupAlarmRequest</td>
					<td><xsl:value-of select="@val"/></td>
				</xsl:when>
				<xsl:when test="@tag='636'">
					<td>WorkingIndicator</td>
					<td><xsl:value-of select="@val"/></td>
				</xsl:when>
				<xsl:when test="@tag='22'">
					<td>SecurityIDSource</td>
					<td><xsl:value-of select="@val"/></td>
				</xsl:when>
				<xsl:when test="@tag='440'">
					<td>ClearingAccount</td>
					<td><xsl:value-of select="@val"/></td>
				</xsl:when>
				<xsl:when test="@tag='439'">
					<td>ClearingFirm</td>
					<td><xsl:value-of select="@val"/></td>
				</xsl:when>
				<xsl:when test="@tag='583'">
					<td>ClOrdLinkID</td>
					<td><xsl:value-of select="@val"/></td>
				</xsl:when>
				<xsl:when test="@tag='432'">
					<td>GoodTilDate</td>
					<td><xsl:value-of select="@val"/></td>
				</xsl:when>
				<xsl:when test="@tag='41'">
					<td>OrigClOrdID</td>
					<td><xsl:value-of select="@val"/></td>
				</xsl:when>
				<xsl:when test="@tag='126'">
					<td>ExpireTime</td>
					<td><xsl:value-of select="@val"/></td>
				</xsl:when>
				<xsl:when test="@tag='122'">
					<td>OrigSendingTime</td>
					<td><xsl:value-of select="@val"/></td>
				</xsl:when>
				<xsl:when test="@tag='43'">
				</xsl:when>					
				<xsl:when test="@tag='851'">
					<td>LastLiquidityInd</td>
					<td><xsl:value-of select="@val"/></td>
				</xsl:when>
			<xsl:otherwise>
				<xsl:call-template name="unknown_tag"/>
			</xsl:otherwise>
		</xsl:choose>
	</xsl:template>

	<xsl:template name="tags_up_to_5999">
		<xsl:choose>
			<xsl:when test="@tag='5006'">
				<td>SessionNo</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='5030'">
				<td>Shared</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:otherwise>
				<xsl:call-template name="unknown_tag"/>
			</xsl:otherwise>
		</xsl:choose>
	</xsl:template>

	<xsl:template name="tags_up_to_6999">
		<xsl:choose>
				<xsl:when test="@tag='6115'">
					<td>TriggerMethod</td>
					<td><xsl:value-of select="@val"/></td>
				</xsl:when>
				<xsl:when test="@tag='6116'">
					<td>IgnoreRth</td>
					<td><xsl:value-of select="@val"/></td>
				</xsl:when>
				<xsl:when test="@tag='6205'">
					<td>OnlyRTH</td>
					<td><xsl:value-of select="@val"/></td>
				</xsl:when>
				<xsl:when test="@tag='6210'">
					<td>TWSTickerExchange</td>
					<td><xsl:value-of select="@val"/></td>
				</xsl:when>
				<xsl:when test="@tag='6236'">
					<td>ExtWorkingIndicator</td>
					<td><xsl:value-of select="@val"/></td>
				</xsl:when>
				<xsl:when test="@tag='6268'">
					<td>TrailingAmtUnit</td>
					<td><xsl:value-of select="@val"/></td>
				</xsl:when>
				<xsl:when test="@tag='6408'">
					<td>PageName</td>
					<td><xsl:value-of select="@val"/></td>
				</xsl:when>
				<xsl:when test="@tag='6419'">
					<td>ClrIntent</td>
					<td><xsl:value-of select="@val"/></td>
				</xsl:when>
				<xsl:when test="@tag='6433'">
					<td>OutsideRTH</td>
					<td><xsl:value-of select="@val"/></td>
				</xsl:when>
				<xsl:when test="@tag='6436'">
					<td>DeactiveOnClose</td>
					<td><xsl:value-of select="@val"/></td>
				</xsl:when>
				<xsl:when test="@tag='6532'">
					<td>CustomerOrderTime</td>
					<td><xsl:value-of select="@val"/></td>
				</xsl:when>
				<xsl:when test="@tag='6568'">
					<td>ExchangeExecID</td>
					<td><xsl:value-of select="@val"/></td>
				</xsl:when>
				<xsl:when test="@tag='6569'">
					<td>ExchangeOrderID</td>
					<td><xsl:value-of select="@val"/></td>
				</xsl:when>
				<xsl:when test="@tag='6571'">
					<td>OrderReceiptTime</td>
					<td><xsl:value-of select="@val"/></td>
				</xsl:when>
				<xsl:when test="@tag='6596'">
					<td>BrokerExpireTime</td>
					<td><xsl:value-of select="@val"/></td>
				</xsl:when>
				<xsl:when test="@tag='6816'">
					<td>FirstExecReceiveTime</td>
					<td><xsl:value-of select="@val"/></td>
				</xsl:when>
				<xsl:when test="@tag='6817'">
					<td>OrigOrderReceiptTime</td>
					<td><xsl:value-of select="@val"/></td>
				</xsl:when>
			<xsl:when test="@tag='6000'">
				<td>InstrumentType</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6001'">
				<td>OptionType</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6002'">
				<td>StrikePrice</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6003'">
				<td>Expiry</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6004'">
				<td>Exchange</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6005'">
				<td>CarryFirm</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6006'">
				<td>CarryFirmSubAccount</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6007'">
				<td>CustFirm</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6008'">
				<td>ContractID</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6009'">
				<td>ConQPath</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6010'">
				<td>OrderReference</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6011'">
				<td>IBRejectReason</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6012'">
				<td>IBStatus</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6013'">
				<td>ExecComponent</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6013'">
				<td>OrderGroup</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6014'">
				<td>IndicativePrice</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6015'">
				<td>OAttrib</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6016'">
				<td>TradeReaderNo</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6017'">
				<td>OCAGroup</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6018'">
				<td>legPath</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6019'">
				<td>NoMarketRules</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6020'">
				<td>MRNegativeCapable</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6021'">
				<td>MRPriceMagnification</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6022'">
				<td>MRNoPriceDisplayIntervals</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6023'">
				<td>MRLowEdge</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6024'">
				<td>MRIntegralDigits</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6025'">
				<td>MRFractionalDigits</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6026'">
				<td>MRNoPriceIncrementIntervals</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6027'">
				<td>MRIncrement</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6028'">
				<td>MRSizeMagnification</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6029'">
				<td>MRNoSizeDisplayIntervals</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6030'">
				<td>MRNoSizeIncrementIntervals</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6031'">
				<td>MRIdent</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6032'">
				<td>MDNosCompressedBits</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6033'">
				<td>MDCompressedData</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6034'">
				<td>TWSVersion</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6035'">
				<td>IBLocalSymbol</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6036'">
				<td>AccountRequest</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6037'">
				<td>OptionOrigin</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6038'">
				<td>LastSecurityDefinition</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6039'">
				<td>BestExEligible</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6040'">
				<td>SubMsgType</td>
				<xsl:choose>
				<xsl:when test="@val='2'">
					<td>LinkageOrderId</td>
				</xsl:when>
				<xsl:when test="@val='3'">
					<td>FairPriceRequest</td>
				</xsl:when>
				<xsl:when test="@val='4'">
					<td>VwapTime</td>
				</xsl:when>
				<xsl:when test="@val='5'">
					<td>SecDefDates</td>
				</xsl:when>
				<xsl:when test="@val='6'">
					<td>AccountRequest</td>
				</xsl:when>
				<xsl:when test="@val='7'">
					<td>CombLegComfirmation</td>
				</xsl:when>
				<xsl:when test="@val='8'">
					<td>MissedMktData</td>
				</xsl:when>
				<xsl:when test="@val='9'">
					<td>SymbolLookupQuery</td>
				</xsl:when>
				<xsl:when test="@val='10'">
					<td>WhatIfMargin</td>
				</xsl:when>
				<xsl:when test="@val='11'">
					<td>Bundle</td>
				</xsl:when>
				<xsl:when test="@val='12'">
					<td>Realloc</td>
				</xsl:when>
				<xsl:when test="@val='13'">
					<td>OptionMoneyQuery</td>
				</xsl:when>
				<xsl:when test="@val='14'">
					<td>Dvp</td>
				</xsl:when>
				<xsl:when test="@val='15'">
					<td>DvpInfo</td>
				</xsl:when>
				<xsl:when test="@val='16'">
					<td>FAPositions</td>
				</xsl:when>
				<xsl:when test="@val='17'">
					<td>DebugInfo</td>
				</xsl:when>
				<xsl:when test="@val='18'">
					<td>UpdateCCPTime</td>
				</xsl:when>
				<xsl:when test="@val='19'">
					<td>XML</td>
				</xsl:when>
				<xsl:when test="@val='20'">
					<td>XML</td>
				</xsl:when>
				<xsl:when test="@val='21'">
					<td>XML</td>
				</xsl:when>
				<xsl:when test="@val='22'">
					<td>XML</td>
				</xsl:when>
				<xsl:when test="@val='23'">
					<td>FAAutoProfile</td>
				</xsl:when>
				<xsl:when test="@val='24'">
					<td>ExcludeFromBest</td>
				</xsl:when>
				<xsl:when test="@val='25'">
					<td>RfqSize</td>
				</xsl:when>
				<xsl:when test="@val='26'">
					<td>DeltaNeutralValidate</td>
				</xsl:when>
				<xsl:when test="@val='30'">
					<td>XmlQuery</td>
				</xsl:when>
				<xsl:otherwise>
					<td><xsl:value-of select="@val"/></td>
				</xsl:otherwise>
				</xsl:choose>	
			</xsl:when>
			<xsl:when test="@tag='6041'">
				<td>ExchPrefs</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6042'">
				<td>LinkageOrderId</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6043'">
				<td>Linkage</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6044'">
				<td>LinkageType</td>
				<xsl:choose>
				<xsl:when test="@val='0'">
					<td>P</td>
				</xsl:when>
				<xsl:when test="@val='1'">
					<td>PA</td>
				</xsl:when>
				<xsl:when test="@val='2'">
					<td>Non-linkage</td>
				</xsl:when>
				<xsl:otherwise>
					<td><xsl:value-of select="@val"/></td>
				</xsl:otherwise>
				</xsl:choose>	
			</xsl:when>
			<xsl:when test="@tag='6045'">
				<td>DpmExchange</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6046'">
				<td>ValidExchanges</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6047'">
				<td>FairPrice</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6048'">
				<td>LeadFutExpConID</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6049'">
				<td>LeadFutExpDate</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6050'">
				<td>DeepExchanges</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6051'">
				<td>ThiAffil</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6052'">
				<td>SystemDefaultSizes</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6053'">
				<td>PrivLabCoName</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6054'">
				<td>PrivLabProdName</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6055'">
				<td>PrivLabFaxNo</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6056'">
				<td>PrivLabUrls</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6057'">
				<td>PrivHelpDesk</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6058'">
				<td>TradingClass</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6059'">
				<td>Reason</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6060'">
				<td>SendResponse</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6061'">
				<td>VwapTime</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6062'">
				<td>Indicative</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6076'">
				<td>BDSymbols</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6083'">
				<td>MaxMktData</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6084'">
				<td>CcpVersion</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6065'">
				<td>MarketPrice</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6067'">
				<td>MarketValue</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6068'">
				<td>Description</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6064'">
				<td>Position</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6088'">
				<td>EOrder</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6091'">
				<td>WhatIf</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6095'">
				<td>AcctCode</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6096'">
				<td>FamilyCode</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6097'">
				<td>Reallocs</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6098'">
				<td>ExecIds</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6077'">
				<td>BrokerDealer</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6105'">
				<td>ActivationPrice</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6106'">
				<td>TrailingClientId</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6107'">
				<td>ParentClientId</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6102'">
				<td>SweepToFill</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6103'">
				<td>Reserved/DisplaySize</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6089'">
				<td>MaxMsgsPerSec</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6090'">
				<td>AnyExchOk</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6102'">
				<td>SweepToFill</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6103'">
				<td>DisplaySize</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6104'">
				<td>LogoFileName</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6105'">
				<td>ActivationPrice</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6106'">
				<td>TrailingClientId</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6107'">
				<td>ParentClientId</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6108'">
				<td>FA</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6131'">
				<td>Submitter</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6117'">
				<td>StopPrice</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6122'">
				<td>OptionAcct</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6123'">
				<td>CondConid</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6124'">
				<td>CondExch</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6125'">
				<td>CondPrice</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6126'">
				<td>CondOp</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6128'">
				<td>CondIgnoreRth</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6130'">
				<td>Chameleon</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6132'">
				<td>PooledAcct</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6136'">
				<td>CondListSize</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6137'">
				<td>CondLogicBind</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6138'">
				<td>Ibsx</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6139'">
				<td>Mibsx</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6140'">
				<td>Sizeop</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6141'">
				<td>PrivLabFrameIconImageName</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6142'">
				<td>PrivLabInitUrl</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6119'">
				<td>ServerId</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6120'">
				<td>ComboRules</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6121'">
				<td>DdeId</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6151'">
				<td>StockRefPrice</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6152'">
				<td>StockRangeLower</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6153'">
				<td>StockRangeUpper</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6154'">
				<td>Delta</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6156'">
				<td>BasketOrder</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6118'">
				<td>XML</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6159'">
				<td>FAMethod</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6160'">
				<td>FAGroup</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6161'">
				<td>FAProfile</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6164'">
				<td>FAPct</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6166'">
				<td>CondStrike</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6168'">
				<td>CondExpiry</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6169'">
				<td>CondSecurityType</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6211'">
				<td>ParentAlertId</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6220'">
				<td>CondContractMultiplier</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6222'">
				<td>CondType</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6223'">
				<td>CondTime</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6224'">
				<td>CondSendEmail</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6226'">
				<td>CondEmailText</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6227'">
				<td>CondTWSActions</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6238'">
				<td>AlertActionOnTrigger</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6241'">
				<td>CondInactive</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6245'">
				<td>CondPercentage</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6246'">
				<td>CondExecutionPattern</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6263'">
				<td>CondMktVolume</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6287'">
				<td>NotHeld</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6289'">
				<td>CurrentPrice</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6521'">
				<td>Deactivate</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6561'">
				<td>TwsAlgoName</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6579'">
				<td>CondSubmitCancel</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6637'">
				<td>ActiveOrderQty</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6661'">
				<td>DeactiveOnDisconnect</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6664'">
				<td>TwsAlgoXml</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='6947'">
				<td>CondTimeZone</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:otherwise>
				<xsl:call-template name="unknown_tag"/>
			</xsl:otherwise>
		</xsl:choose>
	</xsl:template>

	<xsl:template name="tags_up_to_9999">
		<xsl:choose>
			<xsl:when test="@tag='8001'">
				<td>FirstKey</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='8002'">
				<td>SecondKey</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='8003'">
				<td>ThirdKey</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='8004'">
				<td>Value</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='8032'">
				<td>IBKRATS</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='8043'">
				<td>LastTradePrice</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='8109'">
				<td>LastRecvExecTime</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='8339'">
				<td>PriceMgmtAlgo</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>

			<xsl:when test="@tag='8402'">
				<td>Duration</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='8403'">
				<td>EvenMidOffset</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='8404'">
				<td>OddMidOffset</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='8405'">
				<td>PostToATS</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='9131'">
				<td>PriceCheck</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='9130'">
				<td>OrdAction</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='9306'">
				<td>OrigOrderDate</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='9136'">
				<td>QuoteUpdateDesc</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='9137'">
				<td>QuoteRejReason</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='9703'">
				<td>TradingSessionID</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='9702'">
				<td>CtiCode</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='9707'">
				<td>GiveUpFirm</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='9708'">
				<td>CmtaGiveupCD</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='9800'">
				<td>IboTypes</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='9804'">
				<td>Dvp</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='9805'">
				<td>BdType</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='9811'">
				<td>BrokerDealer</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='9805'">
				<td>BDType</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='9804'">
				<td>DVP</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='9812'">
				<td>LastResetTime</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='9813'">
				<td>DiscretionaryAmt</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='9814'">
				<td>Retail</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='9881'">
				<td>BTOrderInst</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='9815'">
				<td>LastLoginTime</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='9801'">
				<td>BlockOrder</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='9817'">
				<td>ConvertToUnderExch</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:when test="@tag='9822'">
				<td>PercentOffset</td>
				<td><xsl:value-of select="@val"/></td>
			</xsl:when>
			<xsl:otherwise>
				<xsl:call-template name="unknown_tag"/>
			</xsl:otherwise>
		</xsl:choose>
	</xsl:template>

	<xsl:template name="unknown_tag">
		<td><xsl:value-of select="@tag"/></td>
		<td><xsl:value-of select="@val"/></td>
	</xsl:template>

</xsl:stylesheet>
