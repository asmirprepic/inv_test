from altintel.data.sample_data import load_proposed_commitment


def test_load_proposed_commitment_reads_source_text() -> None:
    memo = load_proposed_commitment()

    assert memo.fund_name == "Northlake Infrastructure Partners V"
    assert memo.commitment_size_mn == 60.0
    assert "target size is EUR 1,200 million" in memo.source_text
