          # Common IP address part for postscreen regexes
    psIPAddrPart = r'(\S+)(?:\[(\d+\.\d+\.\d+\.\d+)\])?'

    # Postscreen regexes
    rePsConnect = re.compile(r'^CONNECT from ' + psIPAddrPart)
    rePsDNS = re.compile(r'^DNSBL rank \d+ for ' + psIPAddrPart)
    rePsPregreet = re.compile(r'^PREGREET \d+ after [\d.]+ from ' + psIPAddrPart)
    rePsPass = re.compile(r'^PASS (OLD|NEW) ' + psIPAddrPart)
    rePsDisconnect = re.compile(r'^DISCONNECT ' + psIPAddrPart)
    rePsHangup = re.compile(r'^HANGUP after -?[\d.]+ from ' + psIPAddrPart)
    rePsNoqueueRcpt = re.compile(r'^NOQUEUE: reject: RCPT from ' + psIPAddrPart)
    rePsData = re.compile(r'^DATA without valid RCPT from ' + psIPAddrPart)
    rePsBdat = re.compile(r'^BDAT without valid RCPT from ' + psIPAddrPart)
    rePsCmdTimeLimit = re.compile(r'^COMMAND TIME LIMIT from ' + psIPAddrPart)
    rePsCmdLengthLimit = re.compile(r'^COMMAND LENGTH LIMIT from ' + psIPAddrPart)
    rePsBareNewline = re.compile(r'^BARE NEWLINE from ' + psIPAddrPart)
    rePsNonSMTPCmd = re.compile(r'^NON-SMTP COMMAND from ' + psIPAddrPart)
    rePsCmpPipelining = re.compile(r'^COMMAND PIPELINING from ' + psIPAddrPart)
    rePsCmdCountLimit = re.compile(r'^COMMAND COUNT LIMIT from ' + psIPAddrPart)
    rePsNoqueueConnect = re.compile(r'^NOQUEUE: reject: CONNECT from ' + psIPAddrPart)
    rePsListed = re.compile(r'^(DENYLISTED|BLACKLISTED|ALLOWLISTED|WHITELISTED) ' + psIPAddrPart)
    rePsVeto = re.compile(r'^(ALLOWLIST|WHITELIST) VETO ' + psIPAddrPart)

    # Regex patterns
    lmtpPipeSMTPLine = re.compile(r', relay=(\S+), .*, delays=([0-9\.]+)/([0-9\.]+)/([0-9\.]+)/([0-9\.]+), ')
    qmgrInsertLine = re.compile(r'^(?:[A-F0-9]+: )?(?:from=<[^>]+>, )?size=(\d+), nrcpt=(\d+) ')
    qmgrExpiredLine = re.compile(r'^(?:[A-F0-9]+: )?(?:from=<[^>]+>, )?status=(expired|force-expired), returned to sender')
    smtpStatusLine = re.compile(r', status=(\w+) ')
    smtpTLSLine = re.compile(r'^(\S+) TLS connection established to \S+: (\S+) with cipher (\S+) \((\d+)/(\d+) bits\)')
    smtpConnectionTimedOutRe = re.compile(r'^connect\s+to\s+(.*)\[(.*)\]:(\d+):\s+(Connection timed out)$')
    smtpdFCrDNSErrorsLine = re.compile(r'^warning: hostname \S+ does not resolve to address ')
    smtpdProcessesSASLLine = re.compile(r': client=.*, sasl_method=(\S+)')
    smtpdRejectsLine = re.compile(r'^NOQUEUE: reject: RCPT from \S+: ([0-9]+) ')
    smtpdLostConnectionLine = re.compile(r'^lost connection after (\w+) from ')
    smtpdSASLAuthenticationFailuresLine = re.compile(r'^warning: \S+: SASL \S+ authentication failed: ')
    smtpdTLSLine = re.compile(r'^(\S+) TLS connection established from \S+: (\S+) with cipher (\S+) \((\d+)/(\d+) bits\)')
    opendkimSignatureAdded = re.compile(r'^[\w\d]+: DKIM-Signature field added \(s=(\w+), d=(.*)\)$')
    bounceNonDeliveryLine = re.compile(r': sender non-delivery notification: ') 



        self.smtpdSubmissionConnects = Counter('postfix_smtpd_submission_connects_total', 'Total smtpd submission connects')
        self.smtpdSubmissionDisconnects = Counter('postfix_smtpd_submission_disconnects_total', 'Total smtpd submission disconnects')
        self.smtpdSubmissionFCrDNSErrors = Counter('postfix_smtpd_submission_fcrdns_errors_total', 'Total smtpd submission FCrDNS errors')
        self.smtpdSubmissionLostConnections = Counter('postfix_smtpd_submission_lost_connections_total', 'Total smtpd submission lost connections', ['stage'])
        self.smtpdSubmissionProcesses = Counter('postfix_smtpd_submission_processes_total', 'Total smtpd submission processes', ['sasl_method'])
        self.smtpdSubmissionRejects = Counter('postfix_smtpd_submission_rejects_total', 'Total smtpd submission rejects', ['code'])
        self.smtpdSubmissionSASLAuthenticationFailures = Counter('postfix_smtpd_submission_sasl_auth_failures_total', 'Total smtpd submission SASL authentication failures')
        self.smtpdSubmissionTLSConnects = Counter('postfix_smtpd_submission_tls_connects_total', 'Total smtpd submission TLS connects', ['host', 'protocol', 'cipher', 'bits1', 'bits2'])
        self.postscreen = Counter('postfix_postscreen_total', 'Total postscreen events', ['event'])
        self.smtpdConnects = Counter('postfix_smtpd_connects_total', 'Total smtpd connects')
        self.received_counter = Counter('postfix_received_total', 'Total received messages')
        self.sent_counter = Counter('postfix_sent_total', 'Total sent messages')
        self.deferred_counter = Counter('postfix_deferred_total', 'Total deferred messages')
        self.smtpdFCrDNSErrors = Counter('postfix_smtpd_fcrdns_errors_total', 'Total smtpd FCrDNS errors')
        self.cleanupProcesses = Counter('postfix_cleanup_processes_total', 'Total cleanup processes')
        self.cleanupRejects = Counter('postfix_cleanup_rejects_total', 'Total cleanup rejects')
        self.lmtpDelays = Histogram('postfix_lmtp_delays_seconds', 'LMTP delays', ['delay_type'])
        self.pipeDelays = Histogram('postfix_pipe_delays_seconds', 'Pipe delays', ['relay', 'delay_type'])
        self.qmgrInsertsSize = Histogram('postfix_qmgr_inserts_size_bytes', 'QMGR insert sizes')
        self.qmgrInsertsNrcpt = Histogram('postfix_qmgr_inserts_nrcpt', 'QMGR insert nrcpt')
        self.qmgrRemoves = Counter('postfix_qmgr_removes_total', 'Total QMGR removes')
        self.qmgrExpires = Counter('postfix_qmgr_expires_total', 'Total QMGR expires')
        self.smtpDelays = Histogram('postfix_smtp_delays_seconds', 'SMTP delays', ['delay_type'])
        self.smtpProcesses = Counter('postfix_smtp_processes_total', 'Total SMTP processes', ['status'])
        self.smtpStatusDeferred = Counter('postfix_smtp_status_deferred_total', 'Total SMTP deferred statuses')
        self.smtpTLSConnects = Counter('postfix_smtp_tls_connects_total', 'Total SMTP TLS connects', ['host', 'protocol', 'cipher', 'bits1', 'bits2'])
        self.smtpConnectionTimedOut = Counter('postfix_smtp_connection_timed_out_total', 'Total SMTP connection timeouts')
        self.smtpdDisconnects = Counter('postfix_smtpd_disconnects_total', 'Total smtpd disconnects')
        self.smtpdLostConnections = Counter('postfix_smtpd_lost_connections_total', 'Total smtpd lost connections', ['stage'])
        self.smtpdProcesses = Counter('postfix_smtpd_processes_total', 'Total smtpd processes', ['sasl_method'])
        self.smtpdRejects = Counter('postfix_smtpd_rejects_total', 'Total smtpd rejects', ['code'])
        self.smtpdSASLAuthenticationFailures = Counter('postfix_smtpd_sasl_auth_failures_total', 'Total smtpd SASL authentication failures')
        self.smtpdTLSConnects = Counter('postfix_smtpd_tls_connects_total', 'Total smtpd TLS connects', ['host', 'protocol', 'cipher', 'bits1', 'bits2'])
        self.bounceNonDelivery = Counter('postfix_bounce_non_delivery_total', 'Total bounce non-delivery notifications')
        self.virtualDelivered = Counter('postfix_virtual_delivered_total', 'Total virtual delivered')
        self.opendkimSignatureAdded = Counter('postfix_opendkim_signature_added_total', 'Total opendkim signatures added', ['selector', 'domain'])
        self.unsupportedLogEntries = Counter('postfix_unsupported_log_entries_total', 'Total unsupported log entries', ['subprocess', 'level'])
     


    match process:
            case "postfix":
                match subprocess:
                    case "cleanup":

                        if ": message-id=<" in message:
                            self.cleanupProcesses.inc()
                        elif ": reject: " in message:
                            self.cleanupRejects.inc()
                        else:
                            self.add_to_unsupported_line(line, subprocess, level)
                    case "lmtp":
                        lmtpMatches = self.lmtpPipeSMTPLine.match(message)
                        if lmtpMatches:
                            self.add_to_histogram_by_label(self.lmtpDelays, lmtpMatches.group(2), "LMTP pdelay", "before_queue_manager")
                            self.add_to_histogram_by_label(self.lmtpDelays, lmtpMatches.group(3), "LMTP adelay", "queue_manager")
                            self.add_to_histogram_by_label(self.lmtpDelays, lmtpMatches.group(4), "LMTP sdelay", "connection_setup")
                            self.add_to_histogram_by_label(self.lmtpDelays, lmtpMatches.group(5), "LMTP xdelay", "transmission")
                        else:
                            self.add_to_unsupported_line(line, subprocess, level)
                    case "pipe":
                        pipeMatches = self.lmtpPipeSMTPLine.match(message)
                        if pipeMatches:
                            self.add_to_histogram_by_label(self.pipeDelays, pipeMatches.group(2), "PIPE pdelay", pipeMatches.group(1), "before_queue_manager")
                            self.add_to_histogram_by_label(self.pipeDelays, pipeMatches.group(3), "PIPE adelay", pipeMatches.group(1), "queue_manager")
                            self.add_to_histogram_by_label(self.pipeDelays, pipeMatches.group(4), "PIPE sdelay", pipeMatches.group(1), "connection_setup")
                            self.add_to_histogram_by_label(self.pipeDelays, pipeMatches.group(5), "PIPE xdelay", pipeMatches.group(1), "transmission")
                        else:
                            self.add_to_unsupported_line(line, subprocess, level)
                    case "qmgr":
                        print('################# HERE')
                        print(f'message: {message}')
                        qmgrInsertMatches = self.qmgrInsertLine.match(message)
                        if qmgrInsertMatches:

                            print('################# yes')
                            self.add_to_histogram(self.qmgrInsertsSize, qmgrInsertMatches.group(1), "QMGR size")
                            self.add_to_histogram(self.qmgrInsertsNrcpt, qmgrInsertMatches.group(2), "QMGR nrcpt")
                        elif message.endswith(": removed"):
                            self.qmgrRemoves.inc()
                        elif self.qmgrExpiredLine.match(message):
                            self.qmgrExpires.inc()
                        else:
                            self.add_to_unsupported_line(line, subprocess, level)
                    case "smtp":
                        smtpMatches = self.lmtpPipeSMTPLine.match(message)
                        if smtpMatches:
                            self.add_to_histogram_by_label(self.smtpDelays, smtpMatches.group(2), "before_queue_manager", "")
                            self.add_to_histogram_by_label(self.smtpDelays, smtpMatches.group(3), "queue_manager", "")
                            self.add_to_histogram_by_label(self.smtpDelays, smtpMatches.group(4), "connection_setup", "")
                            self.add_to_histogram_by_label(self.smtpDelays, smtpMatches.group(5), "transmission", "")
                            smtpStatusMatches = self.smtpStatusLine.match(message)
                            if smtpStatusMatches:
                                self.smtpProcesses.labels(smtpStatusMatches.group(1)).inc()
                                if smtpStatusMatches.group(1) == "deferred":
                                    self.smtpStatusDeferred.inc()
                        elif smtpTLSMatches := self.smtpTLSLine.match(message):
                            self.smtpTLSConnects.labels(*smtpTLSMatches.groups()).inc()
                        elif smtpMatches := self.smtpConnectionTimedOutRe.match(message):
                            self.smtpConnectionTimedOut.inc()
                        else:
                            self.add_to_unsupported_line(line, subprocess, level)
                    case "smtpd":
                        if message.startswith("connect from "):
                            self.smtpdConnects.inc()
                        elif message.startswith("disconnect from "):
                            self.smtpdDisconnects.inc()
                        elif self.smtpdFCrDNSErrorsLine.match(message):
                            self.smtpdFCrDNSErrors.inc()
                        elif smtpdLostConnectionMatches := self.smtpdLostConnectionLine.match(message):
                            self.smtpdLostConnections.labels(smtpdLostConnectionMatches.group(1)).inc()
                        elif smtpdProcessesSASLMatches := self.smtpdProcessesSASLLine.match(message):
                            self.smtpdProcesses.labels(smtpdProcessesSASLMatches.group(1)).inc()
                        elif ": client=" in message:
                            self.smtpdProcesses.labels("").inc()
                        elif smtpdRejectsMatches := self.smtpdRejectsLine.match(message):
                            self.smtpdRejects.labels(smtpdRejectsMatches.group(1)).inc()
                        elif self.smtpdSASLAuthenticationFailuresLine.match(message):
                            self.smtpdSASLAuthenticationFailures.inc()
                        elif smtpdTLSMatches := self.smtpdTLSLine.match(message):
                            self.smtpdTLSConnects.labels(*smtpdTLSMatches.groups()).inc()
                        else:
                            self.add_to_unsupported_line(line, subprocess, level)
                    case "bounce":
                        bounceMatches = self.bounceNonDeliveryLine.match(message)
                        if bounceMatches:
                            self.bounceNonDelivery.inc()
                        else:
                            self.add_to_unsupported_line(line, process, level)
                    case "virtual":
                        if message.endswith(", status=sent (delivered to maildir)"):
                            self.virtualDelivered.inc()
                        else:
                            self.add_to_unsupported_line(line, process, level)
                    case "postscreen":
                        # Postscreen pattern matching and metric increment
                        found = True
                        if matches := self.rePsConnect.match(message):
                            self.postscreen.labels("CONNECT").inc()
                        elif matches := self.rePsDNS.match(message):
                            self.postscreen.labels("DNSBL").inc()
                        elif matches := self.rePsPregreet.match(message):
                            self.postscreen.labels("PREGREET").inc()
                        elif matches := self.rePsPass.match(message):
                            self.postscreen.labels(f"PASS {matches.group(1)}").inc()
                        elif matches := self.rePsDisconnect.match(message):
                            self.postscreen.labels("DISCONNECT").inc()
                        elif matches := self.rePsHangup.match(message):
                            self.postscreen.labels("HANGUP").inc()
                        elif matches := self.rePsNoqueueRcpt.match(message):
                            self.postscreen.labels("NOQUEUE: RCPT").inc()
                        elif matches := self.rePsData.match(message):
                            self.postscreen.labels("DATA").inc()
                        elif matches := self.rePsBdat.match(message):
                            self.postscreen.labels("BDAT").inc()
                        elif matches := self.rePsCmdTimeLimit.match(message):
                            self.postscreen.labels("COMMAND TIME LIMIT").inc()
                        elif matches := self.rePsCmdLengthLimit.match(message):
                            self.postscreen.labels("COMMAND LENGTH LIMIT").inc()
                        elif matches := self.rePsBareNewline.match(message):
                            self.postscreen.labels("BARE NEWLINE").inc()
                        elif matches := self.rePsNonSMTPCmd.match(message):
                            self.postscreen.labels("NON-SMTP COMMAND").inc()
                        elif matches := self.rePsCmpPipelining.match(message):
                            self.postscreen.labels("COMMAND PIPELINING").inc()
                        elif matches := self.rePsCmdCountLimit.match(message):
                            self.postscreen.labels("COMMAND COUNT LIMIT").inc()
                        elif matches := self.rePsNoqueueConnect.match(message):
                            self.postscreen.labels("NOQUEUE: CONNECT").inc()
                        elif matches := self.rePsListed.match(message):
                            self.postscreen.labels(matches.group(1)).inc()
                        elif matches := self.rePsVeto.match(message):
                            self.postscreen.labels(f"{matches.group(1)} VETO").inc()
                        else:
                            self.add_to_unsupported_line(line, process, level)
                    case "submission/smtpd":
                        if message.startswith("connect from "):
                            self.smtpdSubmissionConnects.inc()
                        elif message.startswith("disconnect from "):
                            self.smtpdSubmissionDisconnects.inc()
                        elif self.smtpdFCrDNSErrorsLine.match(message):
                            self.smtpdSubmissionFCrDNSErrors.inc()
                        elif smtpdLostConnectionMatches := self.smtpdLostConnectionLine.match(message):
                            self.smtpdSubmissionLostConnections.labels(smtpdLostConnectionMatches.group(1)).inc()
                        elif smtpdProcessesSASLMatches := self.smtpdProcessesSASLLine.match(message):
                            self.smtpdSubmissionProcesses.labels(smtpdProcessesSASLMatches.group(1)).inc()
                        elif ": client=" in message:
                            self.smtpdSubmissionProcesses.labels("").inc()
                        elif smtpdRejectsMatches := self.smtpdRejectsLine.match(message):
                            self.smtpdSubmissionRejects.labels(smtpdRejectsMatches.group(1)).inc()
                        elif self.smtpdSASLAuthenticationFailuresLine.match(message):
                            self.smtpdSubmissionSASLAuthenticationFailures.inc()
                        elif smtpdTLSMatches := self.smtpdTLSLine.match(message):
                            self.smtpdSubmissionTLSConnects.labels(*smtpdTLSMatches.groups()).inc()
                        else:
                            self.add_to_unsupported_line(line, process, level)
                    case _:
                        self.add_to_unsupported_line(line, subprocess, level)
            case "opendkim":
                opendkimMatches = self.opendkimSignatureAdded.match(message)
                if opendkimMatches:
                    self.opendkimSignatureAdded.labels(opendkimMatches.group(1), opendkimMatches.group(2)).inc()
                else:
                    self.add_to_unsupported_line(line, process, level)
            case _:
                self.add_to_unsupported_line(line, process, level)