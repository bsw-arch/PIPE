{{/*
Expand the name of the chart.
*/}}
{{- define "pipe-bots.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "pipe-bots.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "pipe-bots.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "pipe-bots.labels" -}}
helm.sh/chart: {{ include "pipe-bots.chart" . }}
{{ include "pipe-bots.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
app.kubernetes.io/part-of: pipe-system
infrastructure: open-source
forbidden.hashicorp/vault: OpenBao
forbidden.hashicorp/consul: Kubernetes
forbidden.hashicorp/terraform: OpenTofu
{{- end }}

{{/*
Selector labels
*/}}
{{- define "pipe-bots.selectorLabels" -}}
app.kubernetes.io/name: {{ include "pipe-bots.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "pipe-bots.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "pipe-bots.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}
