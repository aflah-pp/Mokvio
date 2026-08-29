import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link, useNavigate, useParams } from "react-router-dom";
import { ArrowLeft, Database, Plus, Settings2 } from "lucide-react";

import AppLayout from "@/components/layout/app-layout";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

import { getResource, publishResource, unpublishResource } from "@/service/endpoints/resources";

import { getFields, deleteField } from "@/service/endpoints/fields";

import ResourceFieldsTable from "@/features/resources/components/ResourceFieldsTable";
import ResourceRuntime from "@/features/resources/components/ResourceRuntime";

export default function ResourceDetailPage() {
  const { projectSlug, resourceSlug } = useParams();
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const resourceQuery = useQuery({
    queryKey: ["resources", projectSlug, resourceSlug],
    queryFn: () => getResource(projectSlug, resourceSlug),
    enabled: Boolean(projectSlug && resourceSlug),
    staleTime: 2 * 60 * 1000,
    gcTime: 10 * 60 * 1000,
  });

  const fieldsQuery = useQuery({
    queryKey: ["fields", projectSlug, resourceSlug],
    queryFn: () => getFields(projectSlug, resourceSlug),
    enabled: Boolean(projectSlug && resourceSlug),
    staleTime: 2 * 60 * 1000,
    gcTime: 10 * 60 * 1000,
  });

  const publishMutation = useMutation({
    mutationFn: () =>
      resourceQuery.data?.is_published
        ? unpublishResource(projectSlug, resourceSlug)
        : publishResource(projectSlug, resourceSlug),

    onSuccess: (data) => {
      queryClient.setQueryData(["resources", projectSlug, resourceSlug], data);

      queryClient.invalidateQueries({
        queryKey: ["resources", projectSlug],
      });

      queryClient.invalidateQueries({
        queryKey: ["projects", projectSlug],
      });
    },
  });

  const deleteFieldMutation = useMutation({
    mutationFn: (fieldSlug) => deleteField(projectSlug, resourceSlug, fieldSlug),

    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["fields", projectSlug, resourceSlug],
      });
    },
  });

  const resource = resourceQuery.data;

  const fields = Array.isArray(fieldsQuery.data)
    ? fieldsQuery.data
    : Array.isArray(fieldsQuery.data?.results)
      ? fieldsQuery.data.results
      : [];

  const allowedMethods = resource
    ? [
        resource.get_method && "GET",
        resource.post_method && "POST",
        resource.patch_method && "PATCH",
        resource.delete_method && "DELETE",
      ].filter(Boolean)
    : [];

  const handleCreateField = () => {
    navigate(`/project/${projectSlug}/resources/${resourceSlug}/fields/create`);
  };

  const handleEditField = (field) => {
    navigate(`/project/${projectSlug}/resources/${resourceSlug}/fields/${field.slug}/edit`);
  };

  const handleDeleteField = (field) => {
    deleteFieldMutation.mutate(field.slug);
  };

  if (resourceQuery.isLoading) {
    return (
      <AppLayout>
        <main className="h-[calc(100vh-6rem)] overflow-auto">
          <div className="mx-auto flex min-h-full w-full max-w-5xl items-center justify-center px-4">
            <div className="text-center">
              <p className="font-medium">Loading resource...</p>

              <p className="mt-1 text-sm text-muted-foreground">Fetching resource details.</p>
            </div>
          </div>
        </main>
      </AppLayout>
    );
  }

  if (resourceQuery.isError || !resource) {
    return (
      <AppLayout>
        <main className="h-[calc(100vh-6rem)] overflow-auto">
          <div className="mx-auto w-full max-w-5xl px-4 py-6 sm:px-6 sm:py-8">
            <Button variant="outline" size="sm" asChild>
              <Link to={`/project/${projectSlug}`} className="inline-flex items-center gap-2">
                <ArrowLeft className="size-4" />
                <span>Back to Project</span>
              </Link>
            </Button>

            <Card className="mt-6">
              <CardHeader>
                <CardTitle>Resource not found</CardTitle>

                <CardDescription>
                  {resourceQuery.error?.response?.data?.detail ||
                    "The requested resource does not exist or you do not have access to it."}
                </CardDescription>
              </CardHeader>
            </Card>
          </div>
        </main>
      </AppLayout>
    );
  }

  const isPublishing = publishMutation.isPending;
  const isDeletingField = deleteFieldMutation.isPending;

  return (
    <AppLayout>
      <main className="h-[calc(100vh-6rem)] overflow-auto">
        <div className="mx-auto w-full max-w-6xl px-4 py-6 sm:px-6 sm:py-8 lg:px-8">
          <div className="mb-6 flex items-center justify-between gap-3">
            <Button variant="outline" size="sm" asChild>
              <Link to={`/project/${projectSlug}`} className="inline-flex items-center gap-2">
                <ArrowLeft className="size-4" />
                <span>Back to Project</span>
              </Link>
            </Button>

            <div className="flex items-center gap-2">
              <Button
                variant={resource.is_published ? "outline" : "default"}
                disabled={isPublishing}
                onClick={() => publishMutation.mutate()}
              >
                <Settings2 className="mr-2 size-4" />

                {isPublishing ? "Updating..." : resource.is_published ? "Unpublish" : "Publish"}
              </Button>
            </div>
          </div>

          <div className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
            <div className="flex items-start gap-3">
              <div className="flex size-11 shrink-0 items-center justify-center rounded-lg border bg-muted/40">
                <Database className="size-5 text-muted-foreground" />
              </div>

              <div className="min-w-0">
                <div className="flex flex-wrap items-center gap-2">
                  <h1 className="text-2xl font-bold tracking-tight sm:text-3xl">{resource.name}</h1>

                  <Badge variant={resource.is_published ? "default" : "secondary"}>
                    {resource.is_published ? "Published" : "Draft"}
                  </Badge>
                </div>

                <p className="mt-1 font-mono text-sm text-muted-foreground">/{resource.slug}</p>

                <p className="mt-3 text-sm font-medium">Allowed Methods</p>

                <div className="mt-2 flex flex-wrap gap-2">
                  {allowedMethods.length > 0 ? (
                    allowedMethods.map((method) => (
                      <Badge key={method} variant="outline" className="font-mono">
                        {method}
                      </Badge>
                    ))
                  ) : (
                    <span className="text-sm text-muted-foreground">No methods enabled</span>
                  )}
                </div>
              </div>
            </div>

            <Button onClick={handleCreateField} disabled={isDeletingField}>
              <Plus className="mr-2 size-4" />
              Create Field
            </Button>
          </div>

          {publishMutation.isError && (
            <div className="mb-6 rounded-lg border border-destructive/30 bg-destructive/10 px-4 py-3 text-sm text-destructive">
              {publishMutation.error?.response?.data?.detail || "Failed to update resource status."}
            </div>
          )}

          {deleteFieldMutation.isError && (
            <div className="mb-6 rounded-lg border border-destructive/30 bg-destructive/10 px-4 py-3 text-sm text-destructive">
              {deleteFieldMutation.error?.response?.data?.detail || "Failed to delete field."}
            </div>
          )}

          <div className="grid gap-6 lg:grid-cols-[1fr_360px]">
            <Card>
              <CardHeader>
                <CardTitle>Fields</CardTitle>

                <CardDescription>Define the data generated by this resource.</CardDescription>
              </CardHeader>

              <CardContent className="p-0">
                {fieldsQuery.isLoading ? (
                  <div className="flex min-h-48 items-center justify-center">
                    <div className="text-center">
                      <p className="font-medium">Loading fields...</p>

                      <p className="mt-1 text-sm text-muted-foreground">
                        Fetching resource fields.
                      </p>
                    </div>
                  </div>
                ) : fieldsQuery.isError ? (
                  <div className="flex min-h-48 flex-col items-center justify-center gap-2 px-6 text-center">
                    <p className="font-medium">Failed to load fields</p>

                    <p className="text-sm text-muted-foreground">
                      {fieldsQuery.error?.response?.data?.detail ||
                        "Something went wrong while fetching fields."}
                    </p>

                    <Button size="sm" variant="outline" onClick={() => fieldsQuery.refetch()}>
                      Try Again
                    </Button>
                  </div>
                ) : (
                  <ResourceFieldsTable
                    fields={fields}
                    onEdit={handleEditField}
                    onDelete={handleDeleteField}
                  />
                )}
              </CardContent>
            </Card>

            <ResourceRuntime projectSlug={projectSlug} resource={resource} />
          </div>
        </div>
      </main>
    </AppLayout>
  );
}
