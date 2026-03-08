const BILLING_ENDPOINT = 'http://localhost:8000/internal/test/billing'

const toRequiredInt = (name, value) => {
  const parsed = Number(value)
  if (!Number.isFinite(parsed)) {
    throw new Error(`Expected ${name} to be a finite number, got: ${value}`)
  }
  return parsed
}

export const setUserBillingState = async ({
  email,
  availableTokens,
  lastUsedTokens,
  totalUsedTokens = null,
}) => {
  const hasEmail = typeof email === 'string' && email.trim().length > 0
  if (!hasEmail) {
    throw new Error('setUserBillingState requires email')
  }

  const payload = {
    available_tokens: toRequiredInt('availableTokens', availableTokens),
    last_used_tokens: toRequiredInt('lastUsedTokens', lastUsedTokens),
    total_used_tokens:
      totalUsedTokens === null || totalUsedTokens === undefined
        ? null
        : toRequiredInt('totalUsedTokens', totalUsedTokens),
    email: email.trim(),
  }

  let response
  try {
    response = await fetch(BILLING_ENDPOINT, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
  } catch (error) {
    throw new Error(
      `setUserBillingState failed. Backend not reachable at ${BILLING_ENDPOINT}. ` +
        `Root error: ${error.message}`
    )
  }

  if (!response.ok) {
    const text = await response.text()
    throw new Error(`setUserBillingState failed. Status ${response.status}. Response: ${text}`)
  }

  const data = await response.json()
  if (!data?.user_id) {
    throw new Error('Billing endpoint returned invalid response: missing user_id')
  }
  if (data.available_tokens !== payload.available_tokens) {
    throw new Error(
      `Billing endpoint mismatch: expected available_tokens=${payload.available_tokens}, ` +
        `got ${data.available_tokens}`
    )
  }
  return data
}

export const setSeededDmBilling = async ({
  email,
  availableTokens,
  lastUsedTokens,
  totalUsedTokens = null,
}) => {
  return await setUserBillingState({
    email,
    availableTokens,
    lastUsedTokens,
    totalUsedTokens,
  })
}
