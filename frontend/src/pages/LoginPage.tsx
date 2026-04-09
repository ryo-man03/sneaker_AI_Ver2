// file: src/pages/LoginPage.tsx
import { useState } from 'react'
import type { FormEvent } from 'react'

type LoginPageProps = {
  onLogin: () => void
}

export function LoginPage({ onLogin }: LoginPageProps) {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()

    const normalizedEmail = email.trim()
    const normalizedPassword = password
    if (!normalizedEmail || !normalizedPassword) {
      setError('メールアドレスとパスワードを入力してください。')
      return
    }

    setIsSubmitting(true)
    setError('')

    try {
      const response = await fetch('http://127.0.0.1:8000/api/v1/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: normalizedEmail,
          password: normalizedPassword,
        }),
      })

      if (response.ok) {
        const payload = (await response.json()) as {
          access_token: string
          user_name: string
        }
        localStorage.setItem('sm_access_token', payload.access_token)
        localStorage.setItem('sm_user_name', payload.user_name)
        onLogin()
        return
      }

      const body = (await response.json()) as { detail?: string }
      setError(body.detail ?? 'ログインに失敗しました。資格情報を確認してください。')
    } catch {
      // Scaffold段階ではAPI停止時もUI導線確認を継続できるようにする。
      if (normalizedEmail.includes('@') && normalizedPassword.length >= 1) {
        localStorage.setItem('sm_access_token', 'local-fallback-token')
        localStorage.setItem('sm_user_name', normalizedEmail)
        onLogin()
        return
      }
      setError('ログイン処理に失敗しました。時間をおいて再試行してください。')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <main className="login-wrap">
      <form className="login-card" onSubmit={submit}>
        <h1 className="login-logo">SOLE//MATRIX</h1>
        <p className="login-tagline">SNEAKER INTELLIGENCE PLATFORM</p>
        <label className="form-label" htmlFor="mail">
          メールアドレス
        </label>
        <input
          id="mail"
          className="form-input"
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="you@example.com"
        />
        <label className="form-label" htmlFor="pass">
          パスワード
        </label>
        <input
          id="pass"
          className="form-input"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="••••••••"
        />
        {error ? <p className="form-error">{error}</p> : null}
        <button className="btn-primary" type="submit" disabled={isSubmitting}>
          {isSubmitting ? 'ログイン中...' : 'ログイン → JWT 認証'}
        </button>
      </form>
    </main>
  )
}
