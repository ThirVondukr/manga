
{{- define "api.labels" }}
{{- include "common.labels" . }}
app.kubernetes.io/component: api
{{- end }}

{{- define "api.selectorLabels" }}
{{- include "common.selectorLabels" . }}
app.kubernetes.io/component: api
{{- end }}

{{- define "api.name" }}
{{- include "app.fullname" . }}
{{- end }}

{{- define "api.service.name" -}}
{{- include "app.fullname" . }}
{{- end -}}

{{- define "api.port" -}}
{{ .Values.api.port }}
{{- end -}}

{{- define "api.portName" -}}
http
{{- end -}}

{{- define "api.probePath" -}}
{{ .Values.api.probePath }}
{{- end -}}

{{- define "api.tmpfsVolumeName" -}}
tmpfs
{{- end -}}
