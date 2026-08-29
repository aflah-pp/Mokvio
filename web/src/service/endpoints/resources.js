import api from "../api";

export const getResources = async (projectSlug) => {
  const { data } = await api.get(`/projects/${projectSlug}/resources/`);

  return data;
};

export const getResource = async (projectSlug, resourceSlug) => {
  const { data } = await api.get(`/projects/${projectSlug}/resources/${resourceSlug}/`);

  return data;
};

export const createResource = async (projectSlug, payload) => {
  const { data } = await api.post(`/projects/${projectSlug}/resources/`, payload);
  return data;
};

export const renameResource = async (projectSlug, resourceSlug, payload) => {
  const { data } = await api.patch(
    `/projects/${projectSlug}/resources/${resourceSlug}/rename/`,
    payload,
  );

  return data;
};

export const publishResource = async (projectSlug, resourceSlug) => {
  const { data } = await api.post(`/projects/${projectSlug}/resources/${resourceSlug}/publish/`);

  return data;
};

export const unpublishResource = async (projectSlug, resourceSlug) => {
  const { data } = await api.post(`/projects/${projectSlug}/resources/${resourceSlug}/unpublish/`);

  return data;
};

export const deleteResource = async (projectSlug, resourceSlug) => {
  const { data } = await api.delete(`/projects/${projectSlug}/resources/${resourceSlug}/`);

  return data;
};
