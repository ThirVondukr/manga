{{- define "common.labels" }}
helm.sh/chart: {{ include "application.chart" . }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{ include "common.selectorLabels" . }}
{{- end }}

{{- define "common.selectorLabels" }}
app.kubernetes.io/part-of: {{ include "application.name" . }}
{{- end }}


{{- define "api.labels" }}
{{- include "common.labels" . }}
app.kubernetes.io/component: api
{{- end }}

{{- define "api.selectorLabels" }}
{{- include "common.selectorLabels" . }}
app.kubernetes.io/component: api
{{- end }}

{{- define "migrations.labels" }}
{{ include "common.labels" . }}
app.kubernetes.io/component: migrations
{{- end }}

{{- define "migrations.selectorLabels" }}
{{- include "common.selectorLabels" . }}
app.kubernetes.io/component: migrations
{{- end }}
