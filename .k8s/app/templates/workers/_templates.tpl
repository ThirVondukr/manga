
{{- define "imageResizer.labels" }}
{{- include "common.labels" . }}
app.kubernetes.io/component: image-resizer
{{- end }}

{{- define "imageResizer.selectorLabels" }}
{{- include "common.selectorLabels" . }}
app.kubernetes.io/component: image-resizer
{{- end }}

{{- define "imageResizer.name" }}
{{- include "app.fullname" . }}-image-scaler
{{- end }}
