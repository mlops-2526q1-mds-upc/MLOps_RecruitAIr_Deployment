{{/*
Secret name for dispatcher database credentials
*/}}
{{- define "dispatcher.secretName" -}}
{{ printf "%s-dispatcher-db-credentials" .Release.Name }}
{{- end -}}


{{/*
Dispatcher Database Name
*/}}
{{- define "dispatcher.dbName" -}}
{{ .Values.dispatcher.db.name | default "dispatcher_db" }}
{{- end -}}


{{/*
Dispatcher Database username
*/}}
{{- define "dispatcher.dbUsername" -}}
{{ .Values.dispatcher.db.username | default "dispatcher_user" }}
{{- end -}}


{{/*
Common environment config for dispatcher (database connection)
*/}}
{{- define "dispatcher.env" -}}
- name: RECRUITAIR_DB_USERNAME
  valueFrom:
    secretKeyRef:
      name: {{ include "dispatcher.secretName" . }}
      key: postgres-username
- name: RECRUITAIR_DB_PASSWORD
  valueFrom:
    secretKeyRef:
      name: {{ include "dispatcher.secretName" . }}
      key: postgres-password
- name: RECRUITAIR_DB_HOST
  value: {{ printf "%s-postgres" .Release.Name }}
- name: RECRUITAIR_DB_DATABASE
  value: {{ include "dispatcher.dbName" . }}
- name: RECRUITAIR_DB_PORT
  value: "5432"
{{- end -}}

